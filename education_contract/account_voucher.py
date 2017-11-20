# -*- coding: utf-8 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser


class account_voucher(models.Model):
    _name = 'account.voucher'
    _inherit = 'account.voucher'
    
    education_contract_id = fields.Many2one('education_contract.contract', string='Contrato de estudios')
    plan_id = fields.Many2one('education_contract.plan', string='Plan de pagos')
    payment_term_id = fields.Many2one('education_contract.payment_term', string='Forma de pago')
    
    """def onchange_partner_id(self, cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=None):
        res = super(account_voucher, self).onchange_partner_id(cr, uid, ids, partner_id, journal_id, amount, currency_id, ttype, date, context=context)
        
        import pdb; pdb.set_trace()
        
        print('state?')
        
        res['value'].update({'state': 'draft'})
        
        return res"""
        
        
    """@api.model
    def create(self, vals):
        import pdb; pdb.set_trace()
        
        res = super(account_voucher, self).create(vals)
        
        return res"""
    
        