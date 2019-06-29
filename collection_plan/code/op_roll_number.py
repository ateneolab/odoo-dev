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
