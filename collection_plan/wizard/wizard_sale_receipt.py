# -*- coding: utf-8 -*-

import logging

from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)


class WizardInvoice(models.TransientModel):
    _name = 'collection_plan.wizard_receipt'

    contract_id = fields.Many2one('education_contract.contract', 'Contrato')
    collection_plan_id = fields.Many2one('collection_plan.collection_plan')

    invoice_id = fields.Many2one('account.invoice', string=_(u'Invoices'))
    payment_term_ids = fields.Many2many('education_contract.payment_term', 'wizard_invoice_payment_term',
                                        compute='_compute_payment_terms',
                                        string=_('Payments'))
    partner_id = fields.Many2one('res.partner', related='contract_id.owner', string=_('Customer'))
    operating_unit_id = fields.Many2one('operating.unit', related='contract_id.campus_id',
                                        string=_('Branch office'))
    company_id = fields.Many2one(related='operating_unit_id.company_id', string=_(u'Company'))

    @api.one
    @api.depends('collection_plan_id')
    def _compute_payment_terms(self):
        payment_ids = []

        payment_id = self._context.get('payment_id', False)
        _logger.info('PAYMENT FROM CONTEXT: %s ' % payment_id)

        if not payment_id:
            for inv in self.collection_plan_id.payed_payment_term_ids:
                if not inv.invoice_id:
                    payment_ids.append(inv.id)
        else:
            payment_ids.append(payment_id)

        _logger.info('PAYMENT_IDS: %s' % payment_ids)
        self.payment_term_ids = [(6, 0, payment_ids)]

    @api.multi
    def get_period(self, company_id, date_str, context=None):
        self.ensure_one()

        code = '%s/%s' % (date_str[3:5], date_str[6:])
        domain = [('code', '=', code), ('company_id', '=', company_id)]
        period_id = self.env['account.period'].search(domain)[:1]
        return period_id

    @api.one
    def create_voucher(self):
        if len(self.payment_term_ids):
            pt = self.payment_term_ids[0]
            pt.generate_voucher_receipt('done', self.partner_id.id, self.company_id.id, 'receipt')
            pt.write({'internal_state': 'receipt'})
            res = self.open_voucher(pt.account_voucher_id.id)
            _logger.info('RES TO RETURN FOR OPENING VOUCHER FORM JUST CREATED: %s' % res)
            return res

    @api.multi
    def open_voucher(self, voucher_id):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.pool.get('ir.model.data')
        form_res = ir_model_data.get_object_reference(self._cr, self._uid, 'account_voucher', 'view_voucher_tree')
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(self._cr, self._uid, 'account_voucher', 'view_voucher_form')
        tree_id = tree_res and tree_res[1] or False

        return {
            'name': _('Generated Voucher'),
            'view_type': 'form',
            'view_mode': 'form,tree',
            'res_model': 'account.voucher',
            'res_id': voucher_id,
            'view_id': False,
            'views': [(form_id, 'form'), (tree_id, 'tree')],
            'type': 'ir.actions.act_window',
        }

    @api.multi
    def reconcile_payments(self, inv):
        self.ensure_one()
        for pt in self.payment_term_ids:
            if not pt.account_voucher_id:
                pt.generate_voucher('done')
            inv.write({'payment_id': [(4, pt.account_voucher_id.id)]})
            pt.account_voucher_id.button_proforma_voucher()
        # reconcile payments to update residual
