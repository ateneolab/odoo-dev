# -*- coding: utf-8 -*-

import datetime
import logging

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

_logger = logging.getLogger(__name__)


class WizardInvoice(models.TransientModel):
    _name = 'collection_plan.wizard_invoice'
    _inherit = 'collection_plan.wizard_invoice'

    verification_id = fields.Many2one('education_contract.verification', related='contract_id.verification_id')
    collection_plan_id = fields.Many2one('collection_plan.collection_plan',
                                         related='verification_id.collection_plan_id')
    tax_ids = fields.Many2many('account.tax', string=_('Taxes'))
    taxes_included = fields.Boolean(_(u'Taxes included'))

    @api.multi
    def build_lines(self):
        self.ensure_one()
        inv_lines = []

        tax_ids = []

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

            if self.tax_ids:
                tax_ids = [6, 0, self.tax_ids.ids]
            else:
                for tax in payment.tax_ids:
                    tax_ids = [6, 0, payment.tax_ids.ids]

            # t_domain = [
            #     ('porcentaje', '=', '0'),  # cable, se deberia tomar por parametro, igual se puede editar luego
            #     ('tax_group', '=', 'vat0'),  # cable, se deberia tomar por parametro, igual se puede editar luego
            #     ('company_id', '=', self.operating_unit_id.company_id.id),
            #     ('type_tax_use', 'in', ['sale', 'all'])]
            # tax_id = self.env['account.tax'].search(t_domain)[:1]

            price_unit = 0.0
            taxes = self.tax_ids if self.tax_ids else payment.tax_ids
            for tax in taxes:
                if tax.tax_group == 'vat':
                    factor = tax.porcentaje / 100 + 1
                    if self.taxes_included or payment.taxes_included:
                        price_unit = payment.amount / factor
                    else:
                        price_unit = payment.amount * factor

            line = {
                'name': name,
                'account_id': account.id,
                'price_unit': price_unit or payment.amount,
                'quantity': float(1.0),
                'product_id': default_product.id,
                'invoice_line_tax_id': [(6, 0, tax_ids)],
                'account_analytic_id': False,
            }

            inv_lines.append((0, 0, line))

        return inv_lines

