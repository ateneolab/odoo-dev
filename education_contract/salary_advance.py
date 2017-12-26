# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser


class salary_advance(models.Model):
    _name = 'salary.advance'
    _inherit = 'salary.advance'
    
    is_seller_advance = fields.Boolean(string='Uso de efectivo')
    user_id = fields.Many2one('res.users', related='employee_id.user_id', store=True)
    