# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser

# class education_contract(models.Model):
#     _name = 'education_contract.education_contract'

#     name = fields.Char()

class partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    education_contract_id = fields.One2many('education_contract.contract', 'owner', string='Contrato de estudios')
    display_name = fields.Char(compute='_compute_display_name')
    
    @api.one
    @api.depends('name', 'is_company')
    def _compute_display_name(self):
        self.display_name = self.name
    
    
    def name_get(self,cr,uid,ids,context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr,uid,ids,context)
        
        for object in record_name:
            display_name = object.name
            res.append((object.id, '%s' % (display_name or 'Nombre no visible')))
            
        return res

    @api.model
    def create(self, vals, context=None):
        import pdb; pdb.set_trace()
        if context and 'name' in context:
            name = context.get('name')
            vals.update({'name': name})
        res = super(partner, self).create(vals)
        return res
    