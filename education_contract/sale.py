# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser


class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'
    
    education_contract_id = fields.Many2one('education_contract.contract', string='Contrato de estudios')
    
    def action_button_confirm(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)
        
        if res:
            contract_id = self.generate_education_contract(cr, uid, ids, context=context)
            
            if contract_id:
                self.pool.get('sale.order').write(cr, uid, ids, {'education_contract_id': contract_id})
        
        return res
    
    
    def generate_education_contract(self, cr, uid, ids, context=None):
        
        #try:
        contract_id = self.pool.get('education_contract.contract').create(cr, uid, {'sale_order_id': ids}, context=context)
        return contract_id
        """except Exception, e:
            print('Error creando el Contrato de estudios.')
            return False"""
            
        #return False
        