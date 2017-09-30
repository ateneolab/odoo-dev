# -*- coding: utf-8 -*-

from openerp import models, fields, api

#from openerp.osv import fields, osv

# class show_published_product_price(models.Model):
#     _name = 'show_published_product_price.show_published_product_price'

#     name = fields.Char()

class ProductionLot(models.Model):
    _inherit = 'stock.production.lot'
    _order = 'life_date asc, name, id'

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    pvp = fields.Float(related='product_id.published_sale_price', string='PVP', store=True, digits=(6,4))
    lot_available_qty = fields.Float(string='Disponible en el lote', digits=(6,4))
    
    @api.onchange('lot_id')
    def onchange_lot_id(self):
        quants = self.lot_id.quant_ids
        sum = 0.0
        
        for quant in quants:
            if not quant.reservation_id and quant.location_id.usage in ['internal']:
                sum += quant.qty
                
        self.lot_available_qty = sum
        
    """def product_id_change(self, cr, uid, ids, pricelist, product, lot_id=False, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False, context=None):
    
        # lot_id = self.lot_id
            
        res = super(SaleOrderLine, self).product_id_change(cr, uid, ids, pricelist, product, qty=qty,
            uom=uom, qty_uos=qty_uos, uos=uos, name=name, partner_id=partner_id,
            lang=lang, update_tax=update_tax, date_order=date_order, packaging=packaging, fiscal_position=fiscal_position, flag=flag, context=context)
            
        # res['value']['lot_id'] = lot_id
        
        return res"""
        
        
    """@api.multi
    def product_id_change(self, product, uom_id, qty=0, name='', type='out_invoice', 
            partner_id=False, fposition_id=False, price_unit=False, currency_id=False, 
            company_id=None):
            
        import pdb; pdb.set_trace()
            
        res = super(SaleOrderLine, self).product_id_change(product, uom_id, qty=qty, name=name, type=type, 
            partner_id=partner_id, fposition_id=fposition_id, price_unit=price_unit, currency_id=currency_id, 
            company_id=company_id)
            
        import pdb; pdb.set_trace()
            
        res['value'].update({'lot_id': self.lot_id})
        
        return res"""

    
class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    
    pvp = fields.Float(related='product_id.published_sale_price', string='PVP', store=True, digits=(6,4))
    
    
    
"""class account_aged_trial_balance(osv.osv_memory):
    _inherit = 'account.aged.trial.balance'
    
    def _print_report(self, cr, uid, ids, data, context=None):
        res = {}
        import pdb; pdb.set_trace()
        if context is None:
            context = {}

        data = self.pre_print_report(cr, uid, ids, data, context=context)
        data['form'].update(self.read(cr, uid, ids, ['period_length', 'direction_selection'])[0])

        period_length = data['form']['period_length']
        if period_length<=0:
            raise osv.except_osv(_('User Error!'), _('You must set a period length greater than 0.'))
        if not data['form']['date_from']:
            raise osv.except_osv(_('User Error!'), _('You must set a start date.'))

        start = datetime.strptime(data['form']['date_from'], "%Y-%m-%d")

        if data['form']['direction_selection'] == 'past':
            for i in range(5)[::-1]:
                stop = start - relativedelta(days=period_length)
                res[str(i)] = {
                    'name': (i!=0 and (str((5-(i+1)) * period_length) + '-' + str((5-i) * period_length)) or ('+'+str(4 * period_length))),
                    'stop': start.strftime('%Y-%m-%d'),
                    'start': (i!=0 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop - relativedelta(days=1)
        else:
            for i in range(5):
                stop = start + relativedelta(days=period_length)
                res[str(5-(i+1))] = {
                    'name': (i!=4 and str((i) * period_length)+'-' + str((i+1) * period_length) or ('+'+str(4 * period_length))),
                    'start': start.strftime('%Y-%m-%d'),
                    'stop': (i!=4 and stop.strftime('%Y-%m-%d') or False),
                }
                start = stop + relativedelta(days=1)
        data['form'].update(res)
        if data.get('form',False):
            data['ids']=[data['form'].get('chart_account_id',False)]
        return self.pool['report'].get_action(cr, uid, [], 'account.report_agedpartnerbalance', data=data, context=context)"""