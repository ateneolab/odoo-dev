# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser

# class education_contract(models.Model):
#     _name = 'education_contract.education_contract'

#     name = fields.Char()

class users(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'
    
    contract_conciliation_id = fields.One2many('education_contract.conciliation', 'seller_id', string='Conciliacion de contrato')
    