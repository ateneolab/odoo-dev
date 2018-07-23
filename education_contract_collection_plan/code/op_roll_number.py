# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
import datetime


class RollNumber(models.Model):
    _name = 'op.roll.number'
    _inherit = 'op.roll.number'

    contract_id = fields.Many2one('education_contract.contract', string=u'Education Contract')
    end_date = fields.Date(u'Fecha de terminación', compute='compute_end_date')

    @api.depends('start_date', 'freezing_ids', 'contract_id.verification_id')
    def compute_end_date(self):
        frozen_months = 0.0
        contract_duration = 0.0
        if self.start_date:
            for fi in self.freezing_ids:
                frozen_months += fi.duration
            verification_id = self.env['education_contract.verification'].search(
                [('contract_id', '=', self.contract_id.id)])
            if verification_id:
                contract_duration = verification_id.agreement_duration
            start_date = datetime.datetime.strptime(self.start_date, '%Y-%m-%d')
            months = frozen_months + contract_duration
            end_date = start_date + relativedelta(months=int(months))
            self.end_date = end_date
