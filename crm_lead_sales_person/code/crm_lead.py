# -*- coding: utf-8 -*-

from openerp import models, fields, api


class crm_lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _filter_sales_persons(self):
        return [('id', 'in', [1, 2, 3])]

    user_id = fields.Many2one('res.users', domain=_filter_sales_persons())
