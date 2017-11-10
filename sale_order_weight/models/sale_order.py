# -*- coding: utf-8 -*-
# Copyright 2016 Andrea Cometa - Apulia Software
# License AGPL-3.0 or later (http://www.gnu.org/licenses/gpl.html).

from openerp import models, fields, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    total_weight = fields.Char(compute='_total_weight', string='Peso total', store=True)
    total_volume = fields.Char(string='Volumen total')
    

    @api.multi
    def _total_weight(self):
        """
        Returns total weight from a specified sale order
        """
        lines = self.order_line
        total_weight = 0.0
        for line in lines:
            if line.product_id:
                total_weight += (
                    line.product_id.weight * line.product_uom_qty)
                    
        self.total_weight = total_weight
                    
        return total_weight
        
        
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    cage_qty = fields.Char(string='Cantidad por caja')
    bag_qty = fields.Char(string='Cantidad por funda')
    
    