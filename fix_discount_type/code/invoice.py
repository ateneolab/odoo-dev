# -*- coding: utf-8 -*-

from openerp import models, fields, api
import openerp.addons.decimal_precision as dp


class account_type(models.Model):
    _inherit = 'account.invoice'

    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'), store=True, readonly=True,
                                compute='_compute_amount')

    @api.one
    def do_compute_amount(self):
        if self.discount_view == 'Before Tax':
            if self.discount_type == 'Fixed':
                import pdb; pdb.set_trace()
                the_value_before = self.amount_untaxed - self.discount_value

                tax_amount = 0.0

                if len(self.tax_line):
                    tax = self.tax_line[0]

                    if tax.percent == '12':
                        tax_amount = the_value_before * tax.percent / 100

                self.amount_untaxed = the_value_before
                self.amount_tax = tax_amount
                self.amount_total = self.amount_untaxed + tax_amount

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'retention_id', 'discount_type', 'discount_value',
                 'discount_view')
    def _compute_amount(self):
        res = super(account_type, self)._compute_amount()

        if self.type == 'out_invoice':
            self.do_compute_amount()

    _defaults = {
        'discount_view': 'Before Tax',
        'discount_type': 'Fixed'
    }
