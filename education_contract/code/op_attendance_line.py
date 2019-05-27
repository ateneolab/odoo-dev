# -*- coding: iso-8859-1 -*-

import datetime

from openerp import models, fields, api, _


class OpAttendanceLine(models.Model):
    _name = 'op.attendance.line'
    _inherit = 'op.attendance.line'

    asistencia = fields.Char(
        compute='_compute_asistencia',
        string=_(u'Presente?')
    )

    @api.depends('present')
    def _compute_asistencia(self):
        for record in self:
            if record.present:
                record.asistencia = 'Presente'
            else:
                record.asistencia = 'Ausente'
