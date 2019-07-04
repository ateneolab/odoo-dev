# -*- coding: utf-8 -*-

from openerp import api, fields, models


class OperatingUnit(models.Model):

    _name = "operating.unit"
    _inherit = "operating.unit"

    ir_sequence = fields.Many2one(
        "ir.sequence", string="Sequence", delegate=True, ondelete="cascade"
    )
