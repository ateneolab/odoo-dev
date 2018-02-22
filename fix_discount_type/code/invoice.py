# -*- coding: utf-8 -*-

from openerp import models, fields, api

class account_type(models.Model):
    _inherit = 'account.invoice'

    _defaults = {
        'discount_view': 'Before Tax',
        'discount_type': 'Fixed'
    }