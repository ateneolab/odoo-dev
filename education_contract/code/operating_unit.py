# -*- coding: utf-8 -*-

from openerp import api, fields, models


class OperatingUnit(models.Model):

    _name = "operating.unit"
    _inherit = "operating.unit"
    _inherits = {"ir.sequence": "ir_sequence"}

    ir_sequence = fields.Many2one(
        "ir.sequence",
        string="Sequence",
        delegate=True,
        required=True,
        ondelete="cascade",
    )

    @api.model
    def create(self, vals):
        name = vals["name"]
        seq = self.env["ir.sequence"].create(dict(name=name))
        vals["ir_sequence"] = seq.id
        res = super(OperatingUnit, self).create(vals)
        return res
