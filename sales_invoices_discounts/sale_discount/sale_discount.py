from __future__ import division
from openerp import fields, models, api
import openerp.addons.decimal_precision as dp


class saleorder_discount(models.Model):
    _inherit = 'sale.order'
    discount_view = fields.Selection([('After Tax', 'After Tax'), ('Before Tax', 'Before Tax')], string='Discount Type',
                                     states={'draft': [('readonly', False)]},
                                     help='Choose If After or Before applying Taxes type of the Discount')
    discount_type = fields.Selection([('Fixed', 'Fixed'), ('Percentage', 'Percentage')], string='Discount Method',
                                     states={'draft': [('readonly', False)]})
    discount_value = fields.Float(string='Discount Value', states={'draft': [('readonly', False)]},
                                  help='Choose the value of the Discount')
    discounted_amount = fields.Float(compute='disc_amount', string='Discounted Amount', readonly=True)
    amount_total = fields.Float(string='Total', digits=dp.get_precision('Account'),
                                store=True, readonly=True, compute='_compute_amounts')

    #
    @api.one
    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_value')
    def _compute_amounts(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.order_line)
        val = 0
        for line in self.order_line:
            val += self._amount_line_tax(line)
        if self.discount_view == 'After Tax':
            if self.discount_type == 'Fixed':
                self.amount_total = self.amount_untaxed + val - self.discount_value
            elif self.discount_type == 'Percentage':
                amount_to_dis = (self.amount_untaxed + val) * (self.discount_value / 100)
                self.amount_total = (self.amount_untaxed+ val) - amount_to_dis
            else:
                self.amount_total = self.amount_untaxed + val
        elif self.discount_view == 'Before Tax':
            if self.discount_type == 'Fixed':
                the_value_before = self.amount_untaxed - self.discount_value
                self.amount_total = the_value_before + val
            elif self.discount_type == 'Percentage':
                amount_to_dis = (self.amount_untaxed) * (self.discount_value / 100)
                self.amount_total = self.amount_untaxed + val - amount_to_dis
            else:
                self.amount_total = self.amount_untaxed + val
        else:
            self.amount_total = self.amount_untaxed + val

    @api.one
    @api.depends('order_line.price_subtotal', 'discount_type', 'discount_value')
    def disc_amount(self):
        val = 0
        for line in self.order_line:
            val += self._amount_line_tax(line)
        if self.discount_view == 'After Tax':
            if self.discount_type == 'Fixed':
                self.discounted_amount = self.discount_value
            elif self.discount_type == 'Percentage':
                amount_to_dis = (self.amount_untaxed + val) * (self.discount_value / 100)
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


saleorder_discount()
