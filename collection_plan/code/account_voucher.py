# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class AccountVoucher(models.Model):
    _name = "account.voucher"
    _inherit = "account.voucher"

    voucher_number = fields.Char(string=_(u"No. de recibo"))
