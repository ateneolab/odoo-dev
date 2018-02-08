from __future__ import division
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp
from openerp.tools import amount_to_text_en


class invoice_discount(models.Model):
    _inherit = 'account.invoice'

    discount_view = fields.Selection([('After Tax', 'After Tax'), ('Before Tax', 'Before Tax')], string='Discount Type',
                                     states={'draft': [('readonly', False)]},
                                     help='Choose If After or Before applying Taxes type of the Discount')

    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], string='Discount Method',
                                     states={'draft': [('readonly', False)]},
                                     help='Choose the type of the Discount')
    discount_value = fields.Float(string='Discount Value', states={'draft': [('readonly', False)]},
                                  help='Choose the value of the Discount')
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', readonly=True)
    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_compute_amounts')

    def get_amount(self, amt, row, bow):
        amount_in_word = amount_to_text_en.amount_to_text(amt, row, bow)
        return amount_in_word

    def button_dummy(self, cr, uid, ids, context=None):
        return True

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'discount_type', 'discount_value', 'discount_view')
    def _compute_amounts(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
        self.amount_tax = sum(line.amount for line in self.tax_line)
        if self.discount_view == 'After Tax':
            if self.discount_type == 'Fixed':
                self.amount_total = self.amount_untaxed + self.amount_tax - self.discount_value
            elif self.discount_type == 'Percentage':
                amount_to_dis = (self.amount_untaxed + self.amount_tax) * (self.discount_value / 100)
                self.amount_total = (self.amount_untaxed + self.amount_tax) - amount_to_dis
            else:
                self.amount_total = self.amount_untaxed + self.amount_tax
        elif self.discount_view == 'Before Tax':
            if self.discount_type == 'Fixed':
                the_value_before = self.amount_untaxed - self.discount_value
                self.amount_total = the_value_before + self.amount_tax
            elif self.discount_type == 'Percentage':
                amount_to_dis = (self.amount_untaxed) * (self.discount_value / 100)
                self.amount_total = self.amount_untaxed + self.amount_tax - amount_to_dis
            else:
                self.amount_total = self.amount_untaxed + self.amount_tax
        else:
            self.amount_total = self.amount_untaxed + self.amount_tax

    @api.one
    @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'discount_type', 'discount_value')
    def disc_amount(self):
        if self.discount_view == 'After Tax':
            if self.discount_type == 'Fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'Percentage':
                amount_to_dis = (self.amount_untaxed + self.amount_tax) * (self.discount_value / 100)
                self.discounted_amount = amount_to_dis
            else:
                self.discounted_amount = 0
        elif self.discount_view == 'Before Tax':
            if self.discount_type == 'Fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'Percentage':
                amount_to_dis = self.amount_untaxed * (self.discount_value / 100)
                self.discounted_amount = amount_to_dis
            else:
                self.discounted_amount = 0
        else:
            self.discounted_amount = 0


invoice_discount()
