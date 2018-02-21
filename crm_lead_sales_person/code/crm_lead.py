# -*- coding: utf-8 -*-

from openerp import models, fields, api


class crm_lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def _filter_sales_persons(self):
        users = []

        teams = self.env['crm.case.section'].search([])
        for team in teams:
            users += team.member_ids.ids

        return [('id', 'in', list(set(users)))]

    user_id = fields.Many2one('res.users', domain=_filter_sales_persons)
