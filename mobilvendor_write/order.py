# -*- coding: utf-8 -*-

from openerp import models, fields, api

# class mobilvendor_write(models.Model):
#     _name = 'mobilvendor_write.mobilvendor_write'

#     name = fields.Char()


class pedido(models.Model):
    _inherit = 'sale.order'
    
    code = fields.Char('Codigo de creacion (Mobilvendor)')  # debe existir el campo en Odoo
