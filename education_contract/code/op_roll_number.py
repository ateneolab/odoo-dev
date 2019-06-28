# -*- coding: iso-8859-1 -*-

import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _


class RollNumber(models.Model):
    _name = "op.roll.number"
    _inherit = "op.roll.number"

    beneficiary_id = fields.Many2one("education_contract.beneficiary", string=_("Roll"))
    schedule_reservation_date = fields.Date(u"Fecha de separación de horario")
    start_date = fields.Date(u"Fecha de inicio de clases")
    end_date = fields.Date(u"Fecha de terminación")  # , compute='compute_end_date'
    diploma_date = fields.Date(u"Fecha de entrega de título")
    frozen = fields.Boolean(u"Congelado")
    freezing_ids = fields.One2many(
        "op.roll.number.freeze", "roll_number_id", u"Congelamientos"
    )

    @api.model
    def create(self, vals):
        if not "start_date" in vals:
            vals.update(
                {
                    "start_date": datetime.datetime.today(),
                    # 'active': True
                }
            )
        res = super(RollNumber, self).create(vals)
        return res


class Freeze(models.Model):
    _name = "op.roll.number.freeze"

    start_date = fields.Date(u"Fecha de inicio")
    end_date = fields.Date(u"Fecha fin")
    duration = fields.Integer(u"Duración en meses")
    roll_number_id = fields.Many2one("op.roll.number", u"Matrícula")
