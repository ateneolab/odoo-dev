# -*- coding: utf-8 -*-

from openerp import models, fields, api

class crm_lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def create(self, vals):
        vals['company_id'] = 1

        return super(crm_lead, self).create(vals)

    _defaults = {'company_id': 1}