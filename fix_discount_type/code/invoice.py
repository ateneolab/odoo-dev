# -*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


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

        super(account_type, self)._compute_amount()

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
            self.amount_tax = val2
            self.amount_total = total

    _defaults = {
        # 'discount_view': 'Before Tax',
        'discount_type': 'amount'
    }
