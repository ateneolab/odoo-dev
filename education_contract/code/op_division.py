# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


#### Beneficiary
class Division(models.Model):
    _name = 'op.division'
    _inherit = 'op.division'

    program_id = fields.One2many('education_contract.program', 'division_id', 'Program')
    standard_id = fields.Many2one('op.standard', _(u'Módulo'))
