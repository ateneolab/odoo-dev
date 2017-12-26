# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser
from openerp.exceptions import ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning
import json

import logging
_logger = logging.getLogger(__name__)

#### RPM
class report_rpm(models.TransientModel):
    _name = 'education_contract.rpm_wizard'
    
    manager_id = fields.Many2many('res.users', relation='education_contract_rpm_wizard_manager_user_rel', string='Gerenete de Marketing')
    user_id = fields.Many2many('res.users', string='Vendedor')
    campus_id = fields.Many2many('operating.unit', string='Sucursal')
    date_start = fields.Date('Fecha inicio')
    date_end = fields.Date('Fecha fin')
    contract_ids = fields.Many2many('education_contract.contract', relation='education_contract_rpm_wizard_rel', string='Contratos')
            
    @api.multi
    def print_rpm(self):
        
        domain = [('date', '>=', self.date_start), ('date', '<=', self.date_end)]
        
        if self.user_id:
            domain.append(('user_id', 'in', self.user_id.ids))
            
        if self.manager_id:
            domain.append(('marketing_manager_id', 'in', self.manager_id.ids))
            
        if self.campus_id:
            domain.append(('campus_id', 'in', self.campus_id.ids))
            
        contract_ids = self.env['education_contract.contract'].search(domain)
        self.contract_ids = [(6, False, contract_ids.ids)]
        
        datas = {
            'ids': contract_ids.ids,
            'model': 'education_contract.contract',
            #'form': contract_ids,
        }
        
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'education_contract.report_rpm',
            'datas': datas,
        }
        
            
    def _get_beneficiary_data(self, contract):
        data = []
        
        beneficiary_ids = contract.beneficiary_ids
        
        for b in beneficiary_ids:
            data.append({
                'name': '%s %s %s' % (b.student_id.name, b.student_id.middle_name or '', b.student_id.last_name or '')
            })
            
        return data
        
        
"""class SetEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, set):
            return list(obj)
        
        return json.JSONEncoder.default(self, obj)"""
        
        
"""class report_rpm(models.Model):
    _name = 'education_contract.rpm'
    
    user_id = fields.Char('Vendedor')
    date_start = fields.Char('Fecha inicio')
    date_end = fields.Char('Fecha fin')
    code = fields.Char('Code')"""