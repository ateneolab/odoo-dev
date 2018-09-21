# -*- coding: iso-8859-1 -*-

import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _


class RollNumber(models.Model):
    _name = 'op.roll.number'
    _inherit = 'op.roll.number'

    beneficiary_id = fields.Many2one('education_contract.beneficiary', string=_('Roll'))
    schedule_reservation_date = fields.Date(u'Fecha de separaci�n de horario')
    start_date = fields.Date(u'Fecha de inicio de clases')
    end_date = fields.Date(u'Fecha de terminaci�n')  # , compute='compute_end_date'
    diploma_date = fields.Date(u'Fecha de entrega de t�tulo')
    frozen = fields.Boolean(u'Congelado')
    freezing_ids = fields.One2many('op.roll.number.freeze', 'roll_number_id', u'Congelamientos')

    @api.model
    def create(self, vals):
        if not 'start_date' in vals:
            vals.update({
                'start_date': datetime.datetime.today(),
                # 'active': True
            })
        res = super(RollNumber, self).create(vals)
        return res


class Freeze(models.Model):
    _name = 'op.roll.number.freeze'

    start_date = fields.Date(u'Fecha de inicio')
    end_date = fields.Date(u'Fecha fin', compute='_compute_end_date')
    duration = fields.Integer(u'Duraci�n en meses')
    roll_number_id = fields.Many2one('op.roll.number', u'Matr�cula')

    @api.one
    @api.depends('start_date', 'duration')
    def _compute_end_date(self):
        if self.start_date and self.duration:
            before_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
            self.end_date = before_date + relativedelta(months=self.duration)
        else:
            self.end_date = False
