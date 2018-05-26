# -*- coding: utf-8 -*-

import datetime
import logging

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

_logger = logging.getLogger(__name__)


class WizardInvoice(models.TransientModel):
    _name = 'collection_plan.wizard_invoice'

    invoice_id = fields.Many2one('account.invoice', string=_(u'Invoices'))
    payment_term_ids = fields.Many2many('education_contract.payment_term', 'wizard_invoice_payment_term',
                                        string=_('Payments'))
    partner_id = fields.Many2one('res.partner', string=_('Customer'))
    operating_unit_id = fields.Many2one('operating.unit', string=_('Branch office'))
    company_id = fields.Many2one(related='operating_unit_id.company_id', string=_(u'Company'))

    @api.multi
    def build_lines(self):
        self.ensure_one()

        import pdb
        pdb.set_trace()

        inv_lines = []

        for payment in self.payment_term_ids:
            name = 'Contrato: %s - Fecha de pago: %s' % (
                payment.plan_id.collection_plan_id.contract_id.barcode, payment.payment_date)

            default_product_id = self.env['product.template'].search([('name', '=', 'IMPORT SRI PRODUCT')])
            default_product = self.env['product.product'].search([('product_tmpl_id', '=', default_product_id.id)])

            cm_product_template_util_id = default_product_id.product_template_util_id
            if not cm_product_template_util_id:
                raise _('Accounts for default product is not set correctly for multi company.')

            account = cm_product_template_util_id.account_income
            _logger.info('account_income: %s' % str(account))

            account = self.env['account.account'].sudo().search([
                ('company_id', '=', self.operating_unit_id.company_id.id),
                ('code', '=', account.code)
            ])
            _logger.info('account_income from company: %s' % str(account))

            t_domain = [
                ('porcentaje', '=', '0'),  # cable, se deberia tomar por parametro, igual se puede editar luego
                ('tax_group', '=', 'vat0'),  # cable, se deberia tomar por parametro, igual se puede editar luego
                ('company_id', '=', self.operating_unit_id.company_id.id),
                ('type_tax_use', 'in', ['sale', 'all'])]
            tax_id = self.env['account.tax'].search(t_domain)[:1]

            line = {
                'name': name,
                'account_id': account.id,
                'price_unit': payment.amount,
                'quantity': float(1.0),
                'product_id': default_product.id,
                'invoice_line_tax_id': [(6, 0, [tax_id.id])],
                'account_analytic_id': False,
            }

            inv_lines.append((0, 0, line))

        return inv_lines

    @api.multi
    def build_invoice_data(self, inv_lines):
        company_id = self.operating_unit_id.company_id

        receivable_account_id = company_id.partner_id.property_account_receivable
        if not receivable_account_id:
            raise Exception(_('Payable account for company is not set correctly'))

        if receivable_account_id.company_id.id != company_id:
            receivable_account_id = self.env['account.account'].sudo().search([
                ('code', '=', receivable_account_id.code),
                ('company_id', '=', company_id.id)
            ])

        currency_id = self.env['res.currency'].search([('name', '=', 'USD')])[:1]

        fpos = self.partner_id.property_account_position
        if not fpos:
            raise Exception(_(u'Fiscal position is not configured por partner: %s' % self.partner_id.ced_ruc))

        inv_date = datetime.date.today()

        period_id = self.get_period(company_id.id, inv_date.strftime('%d/%m/%Y'))
        _logger.info('period: %s' % period_id)

        inv_data = {
            'name': 'Factura generada',
            'origin': 'Cobranzas',
            'type': 'out_invoice',
            'reference': False,
            'account_id': receivable_account_id.id,
            'partner_id': self.partner_id.id,
            'invoice_line': inv_lines,
            'currency_id': currency_id.id,
            'comment': '',
            'payment_term': 1,  # CABLE POR AHORA, HAY QUE OBTENERLO
            'fiscal_position': fpos.id,
            'date_invoice': inv_date,
            'date_due': inv_date,
            'company_id': self.company_id.id,
            'period_id': period_id.id,
            'operating_unit_id': self.operating_unit_id.id,
        }

        return inv_data

    @api.multi
    def get_period(self, company_id, date_str, context=None):
        self.ensure_one()

        code = '%s/%s' % (date_str[3:5], date_str[6:])
        domain = [('code', '=', code), ('company_id', '=', company_id)]
        period_id = self.env['account.period'].search(domain)[:1]
        return period_id

    @api.one
    def create_invoice(self):
        inv_obj = self.env['account.invoice']

        import pdb
        pdb.set_trace()

        try:
            inv_lines = self.build_lines()
            inv_data = self.build_invoice_data(inv_lines)

            _logger.info('INVOICE DATA: %s' % inv_data)

            inv = inv_obj.create(inv_data)

            for pt in self.payment_term_ids:
                pt.write({
                    'invoice_id': inv.id
                })

            collection_plan = self.env['collection_plan.collection_plan'].browse(self._context.get('active_ids'))[:1]
            collection_plan.write({
                'invoice_ids': [(4, inv.id)]
            })

        except Exception as e:
            raise except_orm('Error', e)

        ## como cierro el wizard y luego ir directo a la factura creada? ver como lo hace el pedido de venta
