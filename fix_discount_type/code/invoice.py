# -*- coding: utf-8 -*-

from openerp import models, api
from openerp.osv import osv

class account_type(models.Model):
    _inherit = 'account.invoice'

    # An invoice's residual amount is the sum of its unreconciled move lines and,
    # for partially reconciled move lines, their residual amount divided by the
    # number of times this reconciliation is used in an invoice (so we split
    # the residual amount between all invoice)
    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'retention_id')
    def _compute_amount(self):
        disc = 0.0
        for line in self.invoice_line:
            disc += (line.quantity * line.price_unit) * line.discount / 100
        self.amount_discount = disc

        self.compute_amount()

        # super(account_type, self)._compute_amount()

    @api.one
    def compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        for line in self.tax_line:
            if line.tax_group == 'vat':
                self.amount_vat += line.base
                self.amount_tax += line.amount
            elif line.tax_group == 'vat0':
                self.amount_vat_cero += line.base
            elif line.tax_group == 'novat':
                self.amount_novat += line.base
            elif line.tax_group == 'no_ret_ir':
                self.amount_noret_ir += line.base
            elif line.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']:  # estas son las retenciones
                self.amount_tax_retention += line.amount
                if line.tax_group == 'ret_vat_b':  # in ['ret_vat_b', 'ret_vat_srv']:
                    self.amount_tax_ret_vatb += line.base
                    self.taxed_ret_vatb += line.amount
                elif line.tax_group == 'ret_vat_srv':
                    self.amount_tax_ret_vatsrv += line.base
                    self.taxed_ret_vatsrv += line.amount
                elif line.tax_group == 'ret_ir':
                    self.amount_tax_ret_ir += line.base
                    self.taxed_ret_ir += line.amount
            elif line.tax_group == 'ice':
                self.amount_ice += line.amount

        if self.amount_vat == 0 and self.amount_vat_cero == 0:
            self.amount_vat_cero = self.amount_untaxed

        self.amount_total = self.amount_untaxed + self.amount_tax + self.amount_tax_retention
        self.amount_pay = self.amount_tax + self.amount_untaxed

    @api.multi
    def compute_discount(self, discount):  # todo: after taxes
        for inv in self:
            val1 = val2 = 0.0
            disc_amnt = 0.0
            val2 = sum(line.amount for line in self.tax_line)
            for line in inv.invoice_line:
                val1 += (line.quantity * line.price_unit)
                line.discount = discount
                line_disc_amnt = (line.quantity * line.price_unit) * discount / 100
                disc_amnt += line_disc_amnt
                line.discount_amount = line_disc_amnt
            total = val1 + val2 - disc_amnt
            self.amount_discount = disc_amnt

    @api.onchange('discount_type', 'discount_rate')
    def supply_rate(self):
        for inv in self:
            # if inv.discount_rate != 0:
            amount = sum(line.price_subtotal for line in self.invoice_line)
            tax = sum(line.amount for line in self.tax_line)
            if inv.discount_type == 'percent':
                self.compute_discount(inv.discount_rate)
            else:
                total = 0.0
                discount = 0.0
                for line in inv.invoice_line:
                    total += (line.quantity * line.price_unit)
                if inv.discount_rate != 0:
                    discount = (inv.discount_rate / total) * 100
                self.compute_discount(discount)
                # else:
                    # raise osv.except_osv('Error en detalles', u'Especifique todos los precios y las cantidades de los detalles de la factura.')

    _defaults = {
        'discount_type': 'amount'
    }
