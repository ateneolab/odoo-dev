# -*- coding: iso-8859-1 -*-

import datetime

from openerp import models, fields, api, _


class RollNumber(models.Model):
    _name = 'op.roll.number'
    _inherit = 'op.roll.number'

    beneficiary_id = fields.Many2one('education_contract.beneficiary', string=_('Roll'))
    schedule_reservation_date = fields.Date(u'Fecha de separación de horario')
    start_date = fields.Date(u'Fecha de inicio de clases')
    end_date = fields.Date(u'Fecha de terminación')
    diploma_date = fields.Date(u'Fecha de entrega de título')
    # active = fields.Boolean(u'Activo')
    freeze_ids = fields.One2many('op.roll.number.freeze', 'roll_number_id', u'Congelamientos')

    @api.model
    def create(self, vals):
        if not 'start_date' in vals:
            vals.update({
                'start_date': datetime.datetime.today(),
                # 'active': True
            })
        return super(RollNumber, self).create(vals)

    # @api.multi
    # def write(self, vals):
    #     if 'end_date' in vals:
    #         vals.update({
    #             'active': False
    #         })
    #     return super(RollNumber, self).write(vals)


class Freeze(models.Model):
    _name = 'op.roll.number.freeze'

    start_date = fields.Date(u'Fecha de inicio')
    end_date = fields.Date(u'Fecha fin', compute='_compute_end_date')
    duration = fields.Integer(u'Duración en meses')
    roll_number_id = fields.Many2one('op.roll.number', u'Matrícula')

    @api.one
    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        pass
