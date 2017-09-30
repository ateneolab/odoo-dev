# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)

# class l10n_ec_al_retention(models.Model):
#     _name = 'l10n_ec_al_retention.l10n_ec_al_retention'

#     name = fields.Char()


class product(models.Model):
    _inherit = 'product.template'
    
    tax_retention_ids = fields.Many2many('account.tax', string='Retenciones de clientes', domain=[('parent_id','=',False),('tax_group','in',['ret_ir','ret_var_b', 'ret_vat_srv'])])
    supplier_tax_retention_ids = fields.Many2many('account.tax', string='Retenciones para proveedores', domain=[('parent_id','=',False),('tax_group','in',['ret_ir','ret_var_b', 'ret_vat_srv'])])
    

class product(models.Model):
    _inherit = 'product.category'
    
    tax_retention_ids = fields.Many2many('account.tax', string='Retenciones de clientes', domain=[('parent_id','=',False),('tax_group','in',['ret_ir','ret_var_b', 'ret_vat_srv'])])
    supplier_tax_retention_ids = fields.Many2many('account.tax', string='Retenciones para proveedores', domain=[('parent_id','=',False),('tax_group','in',['ret_ir','ret_var_b', 'ret_vat_srv'])])