# -*- coding: utf-8 -*-

from openerp import models, fields, api

class crm_lead(models.Model):
    _inherit = 'crm.lead'


    @api.model
    def filter_sales_persons(self):
        return [1, 2, 3]

    user_id = fields.Many2one('res.users', domain=filter_sales_persons)


