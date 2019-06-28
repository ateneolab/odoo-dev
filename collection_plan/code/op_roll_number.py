# -*- coding: utf-8 -*-

import datetime
from dateutil.relativedelta import relativedelta

from openerp import models, fields, api


class Freeze(models.Model):
    _inherit = "op.roll.number.freeze"

    is_collection = fields.Boolean(
        default=False,
        help="Identifica si el congelamiento fue realizado por una cobranza.",
    )

    @api.one
    @api.depends("start_date", "duration")
    def _compute_end_date(self):
        """En caso de que el congelamiento sea a partir de una cobranza no se
        calcula la fecha de reingreso, toma la que viene de cobranza.
        Esto me permite poder actualizar la fecha de reingreso cuando la cobranza
        sale del estado congelado.
        """
        if not self.is_collection:
            if self.start_date and self.duration:
                before_date = datetime.datetime.strptime(self.start_date, "%Y-%m-%d")
                self.end_date = before_date + relativedelta(months=self.duration)
            else:
                self.end_date = False
