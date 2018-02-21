# -*- coding: utf-8 -*-

from openerp import models, fields, api

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    @api.onchange('section_id')
    def onchange_section_id(self):
        pass