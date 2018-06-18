# -*- coding: utf-8 -*-

import logging

from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)


class PaymentTerm(models.Model):
    _name = 'education_contract.payment_term'
    _inherit = 'education_contract.payment_term'

    invoice_id = fields.Many2one('account.invoice', string=_(u'Invoices'))

    @api.multi
    def confirm_payment(self):
        self.ensure_one()
        self.generate_voucher('done')

    @api.one
    def do_payment(self):
        _logger.info('do_payment')  # raise wizard for payment, then link it to collection plan, contract

    @api.one
    def generate_voucher(self, state, partner_id):
        voucher_data = {
            'partner_id': partner_id,
            'amount': abs(self.amount),
            'journal_id': self.payment_mode_id.journal_id.id,
            'account_id': self.payment_mode_id.journal_id.default_debit_account_id.id,
            'type': 'receipt',
            'reference': self.plan_id.contract_id.barcode,
            'company_id': self.payment_mode_id.journal_id.company_id.id,
        }

        voucher_id = self.env['account.voucher'].create(voucher_data)
        # voucher_id.proforma_voucher()

        self.write({'account_voucher_id': voucher_id.id, 'state': state, 'payed': True})

    @api.multi
    def do_billing(self):
        self.collection_plan_id.update_payed()

        wizard_form = self.env.ref('collection_plan.view_wizard_invoice_form', False)
        view_id = self.env['collection_plan.wizard_invoice']
        new = view_id.create({})
        _logger.info('WIZARD ID: %s' % new.id)
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
            'context': {'payment_id': self.id}
        }
