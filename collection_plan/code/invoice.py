# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class AccountInvoiceLine(models.Model):
    _inherit = "account.invoice.line"

    payment_id = fields.Many2one("education_contract.payment_term", string=_(u"Pagos"))
