# -*- coding: iso-8859-1 -*-

import datetime

from openerp import models, fields, api, _


class Student(models.Model):
    _name = 'op.student'
    _inherit = 'op.student'

    school_support = fields.Boolean(u'Apoyo escolar')
    language_stimulation = fields.Boolean(u'Estimulación del lenguaje')
    notes = fields.Text(u'Notas relacionadas')
    social_club = fields.Char(u'Club social')
    emotional_support = fields.Boolean(u'Apoyo emocional')
    psico_support = fields.Boolean(u'Apoyo psico pedagógico')
