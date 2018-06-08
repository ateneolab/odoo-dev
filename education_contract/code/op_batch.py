# -*- coding: iso-8859-1 -*-

import datetime

from openerp import models, fields, api, _


class Batch(models.Model):
    _name = 'op.batch'
    _inherit = 'op.batch'

    program_id = fields.One2many('education_contract.program', 'batch_id', 'Program')
