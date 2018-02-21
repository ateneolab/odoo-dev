# -*- coding: utf-8 -*-

from openerp import models, fields, api

class crm_lead(models.Model):
    _inherit = 'crm.lead'


    def filter_sales_persons(self):
        return [1, 2, 3]