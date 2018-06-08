# -*- coding: iso-8859-1 -*-

import datetime

from openerp import models, fields, api, _


class RollNumber(models.Model):
    _name = 'op.roll.number'
    _inherit = 'op.roll.number'

    beneficiary_id = fields.Many2one('education_contract.beneficiary', string=_('Roll'))
    start_date = fields.Date(u'Fecha de inicio')
    end_date = fields.Date(u'Fecha de terminación')
    active = fields.Boolean(u'Activo')

    @api.model
    def create(self, vals):
        if not 'start_date' in vals:
            vals.update({
                'start_date': datetime.datetime.today(),
                'active': True
            })
        return super(RollNumber, self).create(vals)

    @api.multi
    def write(self, vals):
        if 'end_date' in vals:
            vals.update({
                'active': False
            })
        return super(RollNumber, self).write(vals)
