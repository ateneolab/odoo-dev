# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class mobilvendor_read(models.Model):
#     _name = 'mobilvendor_read.mobilvendor_read'

#     name = fields.Char()

class mobilvendor_customer(models.Model):
    _inherit = 'res.partner'
    
    code = fields.Char('Codigo Mobilvendor')
    contact_name = fields.Char('Nombre contacto')
    
