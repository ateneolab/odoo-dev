# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


#### Beneficiary
class RollNumber(models.Model):
    _name = 'op.roll.number'
    _inherit = 'op.roll.number'

    beneficiary_id = fields.Many2one('education_contract.beneficiary', string=_('Roll'))