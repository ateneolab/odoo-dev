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
        
class account_retention(models.Model):
    _inherit = 'account.retention'
    
    @api.multi
    def onchange_invoice(self, invoice_id):
        res = super(account_retention, self).onchange_invoice(invoice_id)
        return res
    
    @api.model
    def create(self, vals):
        res = super(account_retention, self).create(vals)

        """if res and 'type' in res['value'] and res['value']['type'] in ['out_invoice']:
            inv = self.env['account.invoice'].browse([invoice_id])
            tids = self.create_tax_lines(inv)
             
            if tids:
                res['value'].update({'tax_ids': [[6, False, tids]]})"""
        
        
        
        inv = res.invoice_id  ####self.env['account.invoice'].browse([res.invoice_id])
        tids = self.create_tax_lines(inv)

        if tids:
            res.write({'tax_ids': [[6, False, tids]]})
        
        """"""
        """if res:
            obj = self.env['account.retention'].browse([res])"""
            
        """if obj.invoice_id and not obj.tax_ids:
            self.create_tax_lines()"""
            
        return res
    
    def create_tax_lines(self, inv):
        
        tids = []
        if inv.type in ['out_invoice']:
            account_invoice_tax_obj = self.env['account.invoice.tax']
            domain = [('invoice_id', '=', inv.id), ('tax_group', 'in', ['ret_ir', 'ret_vat_b', 'ret_vat_srv'])]
            for t in account_invoice_tax_obj.search(domain):
                t.unlink()
        
            inv_lines = inv.invoice_line
            
            tax_grouped = {}
            currency = inv.currency_id.with_context(date=inv.date_invoice or fields.Date.context_today(inv))
            company_currency = inv.company_id.currency_id
            
            
            for line in inv_lines:
                product_id = line.product_id
                
                ###taxes_ids = product_id.taxes_id
                taxes_ids = product_id.tax_retention_ids
                
                taxes = taxes_ids.compute_all(
                    (line.price_unit * (1 - (line.discount or 0.0) / 100.0)),
                    line.quantity, line.product_id, inv.partner_id)['taxes']
                    
                for tax in taxes:
                    if tax['tax_group'] in ['ret_ir', 'ret_vat_b', 'ret_vat_srv']:
                        base = currency.round(tax['price_unit'] * line['quantity'])
                        
                        if tax['tax_group'] in ['ret_vat_b', 'ret_vat_srv']:
                            """vat = account_invoice_tax_obj.search([('invoice_id', '=', inv.id), ('tax_group', 'in', ['vat'])]).ids
                            vat_obj = account_invoice_tax_obj.browse(vat)
                            
                            
                            
                            if vat_obj and len(vat_obj):
                                base = base * vat_obj[0].percent / 100"""
                                
                            base = base * 14 / 100
                    
                        val = {
                            #'invoice_id': inv.id,
                            'name': tax['name'],
                            'amount': tax['amount'],
                            'manual': True,
                            'sequence': tax['sequence'],
                            'base': base,
                            'tax_group': tax['tax_group'],
                        }
                    
                        if inv.type in ('out_invoice'): ## and otra cosa que me diga, esto debe ser opcional
                            val['base_code_id'] = tax['base_code_id']
                            val['tax_code_id'] = tax['tax_code_id']
                            val['base_amount'] = currency.compute(val['base'] * tax['base_sign'], company_currency, round=False)
                            val['tax_amount'] = currency.compute(val['amount'] * tax['tax_sign'], company_currency, round=False)
                            val['account_id'] = tax['account_collected_id'] or line.account_id.id
                            val['account_analytic_id'] = tax['account_analytic_collected_id']
                        else:
                            val['base_code_id'] = tax['ref_base_code_id']
                            val['tax_code_id'] = tax['ref_tax_code_id']
                            val['base_amount'] = currency.compute(val['base'] * tax['ref_base_sign'], company_currency, round=False)
                            val['tax_amount'] = currency.compute(val['amount'] * tax['ref_tax_sign'], company_currency, round=False)
                            val['account_id'] = tax['account_paid_id'] or line.account_id.id
                            val['account_analytic_id'] = tax['account_analytic_paid_id']
                            
                        if not val.get('account_analytic_id') and line.account_analytic_id and val['account_id'] == line.account_id.id:
                            val['account_analytic_id'] = line.account_analytic_id.id
                            
                        key = (val['tax_code_id'], val['base_code_id'], val['account_id'], val['name'])
                        if not key in tax_grouped:
                            tax_grouped[key] = val
                        else:
                            tax_grouped[key]['base'] += val['base']
                            tax_grouped[key]['amount'] += val['amount']
                            tax_grouped[key]['base_amount'] += val['base_amount']
                            tax_grouped[key]['tax_amount'] += val['tax_amount']
            
            
            for t in tax_grouped.values():
                t['base'] = currency.round(t['base'])
                t['amount'] = currency.round(t['amount'])
                t['base_amount'] = currency.round(t['base_amount'])
                t['tax_amount'] = currency.round(t['tax_amount'])
                
                tid = account_invoice_tax_obj.create(t)
                if tid:
                    tids.append(tid.id)

        return tids
        
                
                
    def update_invoice(self, res=None, taxes=None):
        #super(account_retention, self).update_invoice(res)
    
        if not res:
            res = self
            
        if res:
            inv = res.invoice_id
            
            
            ###
            tids = taxes
            ###
            
            if not tids:
                tids = [l.id for l in res.tax_ids if l.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']]  # noqa
            
            account_invoice_tax = self.env['account.invoice.tax'].browse(tids)
            account_invoice_tax.write({'retention_id': res.id, 'num_document': inv.supplier_invoice_number})  # noqa
            
            v_tids = [l.id for l in inv.tax_line if l.tax_group not in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']]  # noqa
            
            ids = tids + v_tids
            inv.write({'tax_line': [[6, False, ids]]})
    
            inv.action_cancel()
            _logger.info('.....Type of the invoice after cancel: ' + inv.type)
            number = inv.supplier_invoice_number
            inv.action_move_create()
            inv.invoice_validate()
            
            """if inv.type in TYPES_TO_VALIDATE:
                res.action_validate(wd_number)"""
                        
            inv.write({'retention_id': res.id, 'number': number})
            
            
    @api.multi
    def action_validate(self, number=None):
        """
        number: Número posible para usar en el documento

        Método que valida el documento, su principal
        accion es numerar el documento segun el parametro number
        """
        for wd in self:
            if wd.to_cancel:
                raise Warning(_('El documento fue marcado para anular.'))
            sequence = wd.invoice_id.journal_id.auth_ret_id.sequence_id
            if wd.internal_number and not number and '/' not in wd.internal_number:
                wd_number = wd.internal_number[6:]
            elif number is None or not number:
                wd_number = self.env['ir.sequence'].get(sequence.code)
                ####wd_number = self.env['ir.sequence'].get_id(sequence.id)  ####
            else:
                wd_number = str(number).zfill(sequence.padding)
            number = '{0}{1}{2}'.format(wd.auth_id.serie_entidad, wd.auth_id.serie_emision, wd_number)
            wd.write({'state': 'done', 'name': number, 'internal_number': number})
            
            self.update_invoice(wd)
        return True
        

"""class account_invoice_tax(models.Model):
    _inherit = 'account.invoice.tax'
    
    @api.model
    def create(self, vals):
        res = super(account_invoice_tax, self).create(vals)
        
        return res"""