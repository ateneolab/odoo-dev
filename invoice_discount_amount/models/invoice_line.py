from openerp import api, models, fields
from openerp.osv import osv
import openerp.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    @api.one
    @api.depends('price_unit', 'discount', 'discount_amount', 'invoice_line_tax_id', 'quantity',
                 'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id')
    def _compute_price(self):
        per_line = False
        if self.invoice_id.discount_scope == 'per_line_before_tax':
            per_line = True

        if per_line:
            if self.invoice_id.discount_type == 'amount':
                discount_factor = self.discount_amount / self.quantity
                price = self.price_unit - discount_factor
                self.discount = 0.0
            elif self.invoice_id.discount_type == 'percent':
                price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        else:
            price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)


        # if not self.discount_amount:
        #     price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        # else:
        #     price = self.price_unit - self.discount_amount
        taxes = self.invoice_line_tax_id.compute_all(price, self.quantity, product=self.product_id,
                                                     partner=self.invoice_id.partner_id)
        self.price_subtotal = taxes['total']
        if self.invoice_id:
            self.price_subtotal = self.invoice_id.currency_id.round(self.price_subtotal)
