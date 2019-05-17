# -*- coding: utf-8 -*-

import datetime
import logging

import math

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

    invoice_id = fields.Many2one('account.invoice', string=_(u'Factura'))
    internal_state = fields.Selection([
        ('created', 'Created'),
        ('invoiced', 'Invoiced'),
        ('receipt', 'Receipt'),
    ], default='created')
    number = fields.Char('Secuencial', compute='_compute_number', store=True)
    company_id = fields.Many2one('res.company', compute='_compute_company', store=True)
    description = fields.Char(u'Description')
    discount = fields.Float(string=_(u'Descuento'))
    discount_type = fields.Selection(
        [
            ('fixed_amount', 'Monto Fijo'),
            ('percentage', 'Porcentage')
        ],
        string=_(u'Tipo de descuento')
    )
    amount_paid = fields.Float(
        string=_(u'Monto a pagar'),
        compute='_compute_amount_to_paid'
    )
    # Use en la vista solamente
    is_discount = fields.Boolean(string=_(u'Descuento'))
    literal = fields.Text(
        string=_(u'Literal'),
        compute='_convert_amount_to_literal'
    )
    quantity = fields.Integer(
        string=_(u'Número de cuota'),
    )

    @api.depends('amount_paid')
    def _convert_amount_to_literal(self):
        for record in self:
            number = record.amount_paid
            literal = record.numero_to_letras(number)
            record.literal = literal

    @api.depends('discount', 'discount_type', 'amount')
    def _compute_amount_to_paid(self):
        for record in self:
            if record.discount:
                if record.discount_type == 'fixed_amount':
                    record.amount_paid = abs(record.amount - record.discount)
                if record.discount_type == 'percentage':
                    record.amount_paid = abs(
                        record.amount - (record.amount * record.discount / 100)
                    )
            else:
                record.amount_paid = record.amount

    @api.one
    @api.depends('account_voucher_id')
    def _compute_number(self):
        if self.account_voucher_id:
            self.number = str(self.id)
        else:
            self.number = ''

    @api.multi
    @api.onchange('description')
    def onchange_description(self):
        pt_id = self.env['education_contract.payment_term'].browse([self._origin.id])
        pt_id.write({'description': self.description})

    @api.multi
    @api.onchange('type', 'cash_sub_type', 'amount', 'check_id', 'voucher_id', 'transfer_id', 'payment_date',
                  'planned_date', 'payed', 'description_other')
    def onchange_fields(self):
        pt_id = self.env['education_contract.payment_term'].browse([self._origin.id])
        pt_id.write({
            'type': self.type,
            'cash_sub_type': self.cash_sub_type,
            'amount': self.amount,
            'check_id': self.check_id.id or False,
            'voucher_id': self.voucher_id.id or False,
            'transfer_id': self.transfer_id.id or False,
            'payment_date': self.payment_date,
            'planned_date': self.planned_date,
            'description_other': self.description_other,
            'payed': self.payed},
        )

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
            'name': _("Generar factura"),
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
            raise except_orm('Error', u'El término de pago no tiene un contrato asociado.')

        partner_id = contract_id.owner
        company_id = contract_id.campus_id.company_id

        self.generate_voucher_receipt('done', partner_id.id, company_id.id, 'receipt')
        self.validate_contract()
        self.plan_id._compute_dues()

    @api.multi
    def do_saling(self):
        self.collection_plan_id.update_payed()

        wizard_form = self.env.ref('collection_plan.view_wizard_reeipt_form', False)
        view_id = self.env['collection_plan.wizard_receipt']
        new = view_id.create({})
        _logger.info('WIZARD ID: %s' % new.id)

        return {
            'name': _("Generar recibo"),
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
