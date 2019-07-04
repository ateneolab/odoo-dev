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
    freezing_ids = fields.One2many(
        "op.roll.number.freeze", "roll_number_id", u"Congelamientos"
    )
    state = fields.Selection(selection_add=[("frozen", u"Congelado")])

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

    @api.onchange("start_date", "duration")
    def onchange_end_date(self):
        if self.start_date and self.duration:
            start_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
            end_date = start_date + relativedelta(months=self.duration)
            self.end_date = end_date

    @api.model
    def create(self, vals):
        """En caso de que el congelamiento sea a partir de una cobranza no se
        calcula la fecha de reingreso, toma la que viene de cobranza.
        Esto me permite poder actualizar la fecha de reingreso cuando la cobranza
        sale del estado congelado.
        """
        if not vals.get("is_collection"):
            if vals.get("start_date") and vals.get("duration"):
                before_date = datetime.datetime.strptime(vals["start_date"], "%Y-%m-%d")
                end_date = before_date + relativedelta(months=vals["duration"])
                vals["end_date"] = end_date
        res = super(Freeze, self).create(vals)
        today = datetime.datetime.today()
        start_date = datetime.datetime.strptime(res.start_date, "%Y-%m-%d")
        end_date = datetime.datetime.strptime(res.end_date, "%Y-%m-%d")
        if today >= start_date and today < end_date:
            res.roll_number_id.state = "frozen"
            res.roll_number_id.date_state = datetime.datetime.today()
        return res

    @api.multi
    def write(self, vals):
        today = datetime.datetime.today()
        if "end_date" in vals:
            start_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
            end_date = vals["end_date"]
            if today >= start_date and today >= end_date:
                self.roll_number_id.state = "active"
                self.roll_number_id.date_state = datetime.datetime.today()
        res = super(Freeze, self).write(vals)
        return res
