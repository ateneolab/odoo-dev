# -*- coding: utf-8 -*-

import datetime
from openerp.exceptions import ValidationError
from openerp import models, fields, api, _


class Student(models.Model):
    _name = "op.student"
    _inherit = "op.student"

    school_support = fields.Boolean(u"Apoyo escolar")
    language_stimulation = fields.Boolean(u"Estimulación del lenguaje")
    notes = fields.Text(u"Notas relacionadas")
    social_club = fields.Char(u"Club social")
    emotional_support = fields.Boolean(u"Apoyo emocional")
    psico_support = fields.Boolean(u"Apoyo psico pedagógico")

    @api.model
    def create(self, vals):
        if "firstname" in vals:
            vals["name"] = vals.get("firstname")
        if "secondname" in vals:
            vals["middle_name"] = vals.get("secondname")
        if "lastname" in vals:
            vals["last_name"] = vals.get("lastname")
        self.check_exist_student(vals)
        res = super(Student, self).create(vals)
        return res

    def check_exist_student(self, vals):
        if "ced_ruc" in vals:
            ced_ruc = vals.get("ced_ruc")
            count = self.search_count([("ced_ruc", "=", ced_ruc)])
            if count > 0:
                raise ValidationError(
                    "Ya existe un estudiante con esa Cédula/RUC/Pasaporte."
                )
