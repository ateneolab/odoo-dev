# -*- coding: utf-8 -*-

import datetime
import logging

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

_logger = logging.getLogger(__name__)


class PaymentTerm(models.Model):
    _name = 'education_contract.payment_term'
    _inherit = 'education_contract.payment_term'

    @api.multi
    def write(self, vals):
        if 'amount' in vals or 'planned_date' in vals:
            if not self.env.user.has_group('collection_plan.group_admin_collection_plan'):
                raise except_orm('Error de acceso',
                                 u'Solo tiene permitido confirmar los pagos. No puede modificar otros datos.')
        return super(PaymentTerm, self).write(vals)

    invoice_id = fields.Many2one('account.invoice', string=_(u'Invoices'))
    internal_state = fields.Selection([
        ('created', 'Created'),
        ('invoiced', 'Invoiced'),
        ('receipt', 'Receipt'),
    ], default='created')
    number = fields.Char('Secuencial')
    company_id = fields.Many2one('res.company', compute='_compute_company', store=True)
    description = fields.Char(u'Description')

    @api.one
    @api.onchange('description')
    def onchange_description(self):
        self.write({'description': self.description})

    @api.one
    @api.depends('plan_id')
    def _compute_company(self):
        company_id = False
        if self.plan_id:
            if self.plan_id.contract_id:
                company_id = self.plan_id.contract_id.campus_id.company_id
            elif self.plan_id.collection_plan_id:
                company_id = self.plan_id.collection_plan_id.contract_id.campus_id.company_id
        self.company_id = company_id
        return company_id

    @api.multi
    def confirm_payment(self):
        self.ensure_one()
        self.generate_voucher('done')

    @api.one
    def do_payment(self):
        _logger.info('do_payment')  # raise wizard for payment, then link it to collection plan, contract

    @api.multi
    def generate_voucher_receipt(self, state, partner_id, company_id, type):
        self.ensure_one()

        journal = self.env['account.journal'].search([
            ('company_id', '=', company_id),
            ('type', '=', self.payment_mode_id.journal_id.type),
            ('default_debit_account_id.code', '=', self.payment_mode_id.journal_id.default_debit_account_id.code),
            ('default_credit_account_id.code', '=', self.payment_mode_id.journal_id.default_credit_account_id.code),
        ])
        # journal = self.payment_mode_id.journal_id
        if not journal:
            raise except_orm('Error', u'Journal is not defined.')

        period = self.env['collection_plan.wizard_invoice'].get_period(company_id,
                                                                       datetime.datetime.today().strftime(
                                                                           '%d/%m/%Y'))

        voucher_data = {
            'partner_id': partner_id,
            'amount': abs(self.amount),
            'journal_id': journal.id,
            'account_id': journal.default_debit_account_id.id,
            'reference': self.plan_id.collection_plan_id.contract_id.barcode,
            'company_id': company_id,
            'type': type,
            'period_id': period.id
        }
        _logger.info('VOUCHER_DATA: %s' % voucher_data)
        voucher_id = self.env['account.voucher'].create(voucher_data)

        partner = self.env['res.partner'].browse([partner_id])
        account_receivable = partner.property_account_receivable
        account_receivable_id = self.env['account.account'].search([
            ('code', '=', account_receivable.code),
            ('company_id', '=', company_id),
        ])

        voucher_line = {
            "name": "",
            # "payment_option": "without_writeoff",
            "amount": abs(self.amount),
            "voucher_id": voucher_id.id,
            "partner_id": partner_id,
            "account_id": account_receivable_id.id,
            "type": "cr",
            'company_id': company_id
        }
        _logger.info('VOUCHER_LINE_DATA: %s' % voucher_line)
        self.env["account.voucher.line"].create(voucher_line)

        # for line in voucher_line_id:
        #     line.write({'period_id': period.id})

        voucher_id.signal_workflow("proforma_voucher")

        self.write({'account_voucher_id': voucher_id.id, 'state': state, 'payed': True})

    @api.one
    def generate_voucher(self, state, partner_id, company_id, type, invoice):
        journal = self.env['account.journal'].search([
            ('company_id', '=', company_id),
            ('type', '=', self.payment_mode_id.journal_id.type),
            ('default_debit_account_id.code', '=', self.payment_mode_id.journal_id.default_debit_account_id.code),
            ('default_credit_account_id.code', '=', self.payment_mode_id.journal_id.default_credit_account_id.code),
        ])
        if not journal:
            raise except_orm('Error', u'Journal is not defined.')

        voucher_data = {
            'partner_id': partner_id,
            'amount': abs(self.amount),
            'journal_id': journal.id,
            'account_id': journal.default_debit_account_id.id,
            'reference': self.plan_id.collection_plan_id.contract_id.barcode,
            'company_id': company_id,
            'type': type,
            'period_id': invoice.period_id.id
        }
        _logger.info('VOUCHER_DATA: %s' % voucher_data)
        voucher_id = self.env['account.voucher'].create(voucher_data)
        _logger.info('COMPANY: %s, invoice move company: %s' % (company_id, invoice.move_id.line_id[0].company_id))

        voucher_line = {
            "name": "",
            "payment_option": "without_writeoff",
            "amount": abs(self.amount),
            "voucher_id": voucher_id.id,
            "partner_id": partner_id,
            "account_id": invoice.move_id.line_id[0].account_id.id,
            "type": "cr",
            "move_line_id": invoice.move_id.line_id[0].id,
            'company_id': company_id
        }
        _logger.info('VOUCHER_LINE_DATA: %s' % voucher_line)
        voucher_line_id = self.env["account.voucher.line"].create(voucher_line)

        for line in voucher_line_id:
            line.write({'period_id': invoice.period_id.id})

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

    @api.one
    def confirm(self):
        contract_id = self.plan_id.contract_id or self.plan_id.collection_plan_id.contract_id
        if not contract_id:
            raise except_orm('Error', u'El trémino de pago no tiene un contrato asociado.')

        partner_id = contract_id.owner
        company_id = contract_id.campus_id.company_id

        self.generate_voucher_receipt('done', partner_id.id, company_id.id, 'receipt')
        self.validate_contract()

    @api.multi
    def do_saling(self):
        self.collection_plan_id.update_payed()

        wizard_form = self.env.ref('collection_plan.view_wizard_reeipt_form', False)
        view_id = self.env['collection_plan.wizard_receipt']
        new = view_id.create({})
        _logger.info('WIZARD ID: %s' % new.id)
        return {
            'name': _("Generate voucher"),
            'type': 'ir.actions.act_window',
            'res_model': 'collection_plan.wizard_receipt',
            'res_id': new.id,
            'view_id': wizard_form.id,
            'view_mode': 'form',
            'view_type': 'form',
            'nodestroy': True,
            'target': 'new',
            'context': {'payment_id': self.id}
        }

    @api.multi
    def print_receipt(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'collection_plan.report_receipt_template',
            'context': self._context,
        }
