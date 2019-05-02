# -*- coding: iso-8859-1 -*-

import datetime

from openerp import models, fields, api, _


class Standard(models.Model):
    _name = 'op.standard'
    _inherit = 'op.standard'

    program_id = fields.One2many('education_contract.program', 'standard_id', 'Program')
