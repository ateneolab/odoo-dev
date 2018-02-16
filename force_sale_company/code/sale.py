# -*- coding: utf-8 -*-

from openerp import models, fields, api

class sale_order(models.Model):
    _inherit = 'sale.order'

    @api.model
    def create(self, vals):
        vals['company_id'] = 1
        vals['warehouse_id'] = 1

        return super(sale_order, self).create(vals)

    _defaults = {'company_id': 1, 'warehouse_id': 1}