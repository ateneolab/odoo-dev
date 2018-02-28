from openerp import api, models, fields
from openerp.osv import osv
import openerp.addons.decimal_precision as dp


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    discount_amount = fields.Float(string='Discount amount',
                                   digits=(16, 10),
                                   # digits= dp.get_precision('Discount'),
                                   default=0.0)

