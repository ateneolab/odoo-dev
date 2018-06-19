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
    def generate_voucher(self, state, partner_id, company_id, type, invoice):
        voucher_data = {
            'partner_id': partner_id,
            'amount': abs(self.amount),
            'journal_id': self.payment_mode_id.journal_id.id,
            'account_id': self.payment_mode_id.journal_id.default_debit_account_id.id,
            'reference': self.plan_id.collection_plan_id.contract_id.barcode,
            'company_id': company_id,
            'type': type,
        }
        _logger.info('VOUCHER_DATA: %s' % voucher_data)
        voucher_id = self.env['account.voucher'].create(voucher_data)

        voucher_line = {
            "name": "",
            "payment_option": "without_writeoff",
            "amount": abs(self.amount),
            "voucher_id": voucher_id.id,
            "partner_id": partner_id,
            "account_id": self.payment_mode_id.journal_id.default_debit_account_id.id,
            "type": "cr",
            "move_line_id": invoice.move_id.line_id[0].id,
            'company_id': company_id
        }
        _logger.info('VOUCHER_LINE_DATA: %s' % voucher_line)
        self.env["account.voucher.line"].create(voucher_line)

        voucher_id.signal_workflow("proforma_voucher")

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

class Voucher(models.Model):
    _name = 'account.voucher'
    _inherit = 'account.voucher'

    def action_move_line_create(self, cr, uid, ids, context=None):
        '''
        Confirm the vouchers given in ids and create the journal entries for each of them
        '''
        if context is None:
            context = {}
        move_pool = self.pool.get('account.move')
        move_line_pool = self.pool.get('account.move.line')
        for voucher in self.browse(cr, uid, ids, context=context):
            local_context = dict(context, force_company=voucher.journal_id.company_id.id)
            if voucher.move_id:
                continue
            company_currency = self._get_company_currency(cr, uid, voucher.id, context)
            current_currency = self._get_current_currency(cr, uid, voucher.id, context)
            # we select the context to use accordingly if it's a multicurrency case or not
            context = self._sel_context(cr, uid, voucher.id, context)
            # But for the operations made by _convert_amount, we always need to give the date in the context
            ctx = context.copy()
            ctx.update({'date': voucher.date})
            # Create the account move record.
            move_id = move_pool.create(cr, uid, self.account_move_get(cr, uid, voucher.id, context=context), context=context)
            # Get the name of the account_move just created
            name = move_pool.browse(cr, uid, move_id, context=context).name
            # Create the first line of the voucher
            move_line_id = move_line_pool.create(cr, uid, self.first_move_line_get(cr,uid,voucher.id, move_id, company_currency, current_currency, local_context), local_context)
            move_line_brw = move_line_pool.browse(cr, uid, move_line_id, context=context)
            line_total = move_line_brw.debit - move_line_brw.credit
            rec_list_ids = []
            if voucher.type == 'sale':
                line_total = line_total - self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            elif voucher.type == 'purchase':
                line_total = line_total + self._convert_amount(cr, uid, voucher.tax_amount, voucher.id, context=ctx)
            # Create one move line per voucher line where amount is not 0.0
            line_total, rec_list_ids = self.voucher_move_line_create(cr, uid, voucher.id, line_total, move_id, company_currency, current_currency, context)

            # Create the writeoff line if needed
            ml_writeoff = self.writeoff_move_line_get(cr, uid, voucher.id, line_total, move_id, name, company_currency, current_currency, local_context)
            if ml_writeoff:
                move_line_pool.create(cr, uid, ml_writeoff, local_context)
            # We post the voucher.
            self.write(cr, uid, [voucher.id], {
                'move_id': move_id,
                'state': 'posted',
                'number': name,
            })
            if voucher.journal_id.entry_posted:
                move_pool.post(cr, uid, [move_id], context={})
            # We automatically reconcile the account move lines.
            reconcile = False
            for rec_ids in rec_list_ids:
                if len(rec_ids) >= 2:
                    reconcile = move_line_pool.reconcile_partial(cr, uid, rec_ids, writeoff_acc_id=voucher.writeoff_acc_id.id, writeoff_period_id=voucher.period_id.id, writeoff_journal_id=voucher.journal_id.id)
        return True