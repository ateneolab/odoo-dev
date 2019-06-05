# -*- coding: utf-8 -*-

from openerp import models, fields


class OpAttendanceSheet(models.Model):
    _name = "op.attendance.sheet"
    _inherit = "op.attendance.sheet"

    name = fields.Char("Name", size=150)
