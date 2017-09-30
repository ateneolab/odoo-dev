# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api
import logging
_logger = logging.getLogger(__name__)

# class l10n_ec_al_retention(models.Model):
#     _name = 'l10n_ec_al_retention.l10n_ec_al_retention'

#     name = fields.Char()

"""class account_invoice(models.Model):    
    _inherit = 'account.invoice'
    
    def invoice_validate(self, cr, uid, ids, context=None):
        res = super(account_invoice, self).invoice_validate(cr, uid, ids, context=context)
        return res"""
        
class account_tax(models.Model):
    _inherit = 'account.tax'
    
    def name_get(self, cr, uid, ids, context=None):
        if not ids:
            return []
        res = []
        for record in self.read(cr, uid, ids, ['description','name'], context=context):
            #name = record['description'] and record['description'] or record['name']
            desc = record['description'] or ''
            name = record['name'] or ''
            name = '%s-%s' % (desc, name)
            res.append((record['id'],name ))
        return res