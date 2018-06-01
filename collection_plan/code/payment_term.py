# -*- coding: utf-8 -*-

import logging

from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)


class PaymentTerm(models.Model):
    _name = 'education_contract.payment_term'
    _inherit = 'education_contract.payment_term'

    invoice_id = fields.Many2one('account.invoice', string=_(u'Invoices'))

    @api.one
    def confirm_payment(self):
        self.generate_voucher('done')

    @api.one
    def do_payment(self):
        _logger.info('do_payment')

    @api.one
    def generate_voucher(self, state):
        voucher_data = {
            'partner_id': self.plan_id.contract_id.owner.id,
            'amount': abs(self.amount),
            'journal_id': self.payment_mode_id.journal_id.id,
            'account_id': self.payment_mode_id.journal_id.default_debit_account_id.id,
            'type': 'receipt',
            'reference': self.plan_id.contract_id.barcode,
            'company_id': self.payment_mode_id.journal_id.company_id.id,
        }

        voucher_id = self.env['account.voucher'].create(voucher_data)
        voucher_id.proforma_voucher()

        self.write({'account_voucher_id': voucher_id.id, 'state': state})

    @api.multi
    def do_billing(self):
        self.update_payed()

        wizard_form = self.env.ref('collection_plan.view_wizard_invoice_form', False)
        view_id = self.env['collection_plan.wizard_invoice']
        new = view_id.create({})
        return {
            'name': _("Generate invoice"),
            'type': 'ir.actions.act_window',
            'res_model': 'collection_plan.wizard_invoice',
            'res_id': new.id,
            'view_id': wizard_form.id,
            'view_mode': 'form',
            'view_type': 'form',
            'nodestroy': True,
            'target': 'new',
        }
    #
    # @api.one
    # @api.depends('collection_plan_id')
    # def _compute_payment_terms(self):
    #     inv_ids = []
    #     for inv in self.collection_plan_id.payed_payment_term_ids:
    #         if not inv.invoice_id:
    #             inv_ids.append(inv.id)
    #     self.payment_term_ids = [(6, 0, inv_ids)]
    #     # self.payment_term_ids = [(6, 0, self.collection_plan_id.payed_payment_term_ids.ids)]
