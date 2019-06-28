# -*- coding: utf-8 -*-

from openerp import models, fields


class Freeze(models.Model):
    _inherit = "op.roll.number.freeze"

    is_collection = fields.Boolean(
        help="Identifica si el congelamiento fue realizado por una cobranza."
    )
