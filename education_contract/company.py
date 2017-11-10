# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser


class res_company(models.Model):
    _name = 'res.company'
    _inherit = 'res.company'
    
    marketing_manager_id = fields.Many2one('res.users', string='Gerente de Marketing')
    
