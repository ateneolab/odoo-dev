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
    