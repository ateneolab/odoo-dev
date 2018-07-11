# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api, _


class RollNumber(models.Model):
    _name = 'op.roll.number'
    _inherit = 'op.roll.number'

    contract_id = fields.Many2one('education_contract.contract', string=u'Education Contract')
