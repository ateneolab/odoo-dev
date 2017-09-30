# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime

import logging
_logger = logging.getLogger(__name__)


class mobilvendor_customer(models.Model):
    _name = 'mobilvendor_write.cron_mobilvendor_write'
    
    name = fields.Char(required=True)
    numberOfUpdates = fields.Integer('Number of updates', help='The number of times the scheduler has run and updated this field')
    lastModified = fields.Char('Last updated time')
    lastStartModified = fields.Char('Before last updated time')
    meanTime = fields.Float('Tiempo transcurrido desde la ultima actualizacion', digits=(4,2))
    
    def process_mobilvendor_write_scheduler_queue(self, cr, uid, context=None):
        _logger.info("......El cron: Actualizar informacion que escribe Mobilvendor - scheduler corriendo...")
        _logger.info("Start time: %s." % datetime.datetime.now())
        
        lastStartModified = False
        
        self.update_pedidos(cr, uid, context=context)
        
    def update_pedidos(self, cr, uid, context=None):
        _logger.info("....Update Pedidos data from MobilVendor integrator...")
        
        cr.execute("""SELECT * FROM pedidos_cab WHERE read = 0""")
        order_ids = cr.fetchall()
        
        ids = []
        to_delete = []
        
        for so in order_ids:
            ids.append({
                'tipo': so[0],
                'bodega': so[1],
                'numero': so[2],  # numero de orden
                'secuencial': so[3],
                'cliente': so[4],
                'vendedor': so[5],
                'fecha': so[6],
                'estado': so[7],
                'subtotal': so[8],
                'descuento': so[9],
                'iva': so[10],
                'neto': so[11],
                'peso': so[12],
                'volumen': so[13],
                'operador': so[14],
                'comentario': so[15],
                'observacion': so[16],
                'fechacrea': so[17],
                'cltnuevo': so[18],
                'codigomovil': so[19],
                'price_list_code': so[20],
            })
            to_delete.append(so[3])
            
        lines_ids = []
            
        for id in ids:
            cr.execute("""select * from pedidos_lin where secuencial = %s""" % id['secuencial'])
            lines = cr.fetchall()
            
            if len(lines):
                new_sale_order = self.create_sale_order(cr, uid, id, context=context)
                
                for line in lines:
                    self.create_new_line(cr, uid, new_sale_order, line, context=context)
                    lines_ids.append(line[1])
                    
        if len(lines_ids):
            cad = str(tuple(to_delete))
            last = cad.rfind(',')
            cad = '%s)' % cad[:last]
            ####cr.execute("""UPDATE pedidos_cab SET read = 1 where secuencial in """ + str(tuple(lines_ids)))
            cr.execute("""UPDATE pedidos_cab SET read = 1 where secuencial in """ + cad)

        
    def create_new_line(self, cr, uid, new_sale_order, line, context=None):
        env = self.pool.get('sale.order')
        sol_env = self.pool.get('sale.order.line')
        p_env = self.pool.get('product.product')
        t_env = self.pool.get('account.tax')
        
        product_id = p_env.search(cr, uid, [('id', '=', line[2])])
        if not product_id or not len(product_id):
            return False
        product_id = product_id[0]
        product_obj = p_env.browse(cr, uid, [product_id], context=context)
        
        product_uom_qty = line[4]  # revisar con mv que solo pongan la cantiad en este campo (esto es un cable)
        price_unit = line[6]
        
        iva_id = t_env.search(cr, uid, [('tax_group', 'in', ['vat']), ('type_tax_use', 'in', ['sale']), ('porcentaje', '=', 12)])
        if not iva_id or not len(iva_id):
            return False
        iva_id = iva_id[0]
        
        data = {
            'product_id': product_id,
            'product_uom_qty': product_uom_qty,
            'price_unit': price_unit,
            'tax_id': [[6, False, [iva_id]]],
            'name': '[%s] %s' % (product_obj.ean13 if product_obj.ean13 else product_obj.default_code, product_obj.name_template),
            'order_id': new_sale_order,
            'discount': line[16],
            'cage_qty': line[3],
            'bag_qty': line[5],
        }
        
        new_line = sol_env.create(cr, uid, data, context=context)
        
        
    def create_sale_order(self, cr, uid, saleorder, context=None):
        env = self.pool.get('sale.order')
        p_env = self.pool.get('res.partner')
        sol_env = self.pool.get('sale.order.line')
        wh_env = self.pool.get('stock.warehouse')
        pl_env = self.pool.get('product.pricelist')
        user_env = self.pool.get('res.users')
        
        customer = p_env.search(cr, uid, [('ced_ruc', '=', saleorder['cliente'])])
        if not customer or not len(customer):
            return False  # tratar estos incidentes
        
        # If here, Customer was found: partner_id, partner_shipping_id, partner_invoice_id
        partner_id = customer[0]
        
        bodega = wh_env.search(cr, uid, [('id', '=', saleorder['bodega'])])
        if not bodega or not len(bodega):
            return False  # tratar estos incidentes
            
        # If here, Warehouse was found: warehouse_id
        warehouse_id = bodega[0]
        
        price_list = pl_env.search(cr, uid, [('id', '=', saleorder['price_list_code'])])
        if not price_list or not len(price_list):
            return False  # tratar estos incidentes
            
        # If here, Price_list was found: pricelist_id
        pricelist_id = price_list[0]
        
        seller = user_env.search(cr, uid, [('ced_ruc', '=', saleorder['vendedor'])])
        if not seller or not len(seller):
            return False  # tratar estos incidentes
            
        # If here, Vendedor was found: user_id
        user_id = seller[0]
        
        sale_order_data = {
            'partner_id': partner_id,
            'partner_shipping_id': partner_id,
            'partner_invoice_id': partner_id,
            'warehouse_id': warehouse_id,
            'pricelist_id': pricelist_id,  # cable por ahora
            'user_id': user_id,
            'note': saleorder['comentario'],
            'amount_untaxed': saleorder['subtotal'],
            'amount_tax': saleorder['iva'],
            'amount_total': saleorder['neto'],
            'total_weight': saleorder['peso'],
            'total_volume': saleorder['volumen'],
        }
        
        new_sale_order = env.create(cr, uid, sale_order_data)
        
        return new_sale_order
        
        
"""class sale_order_line(models.Model):
    _inherit = 'sale.order.line'
    
    def create(self, cr, uid, values, context=None):
        import pdb; pdb.set_trace()
        if values.get('order_id') and values.get('product_id') and  any(f not in values for f in ['name', 'price_unit', 'product_uom_qty', 'product_uom']):
            import pdb; pdb.set_trace()
            order = self.pool['sale.order'].read(cr, uid, values['order_id'], ['pricelist_id', 'partner_id', 'date_order', 'fiscal_position'], context=context)
            defaults = self.product_id_change(cr, uid, [], order['pricelist_id'][0], values['product_id'],
                qty=float(values.get('product_uom_qty', False)),
                uom=values.get('product_uom', False),
                qty_uos=float(values.get('product_uos_qty', False)),
                uos=values.get('product_uos', False),
                name=values.get('name', False),
                partner_id=order['partner_id'][0],
                date_order=order['date_order'],
                fiscal_position=order['fiscal_position'][0] if order['fiscal_position'] else False,
                flag=False,  # Force name update
                context=dict(context or {}, company_id=values.get('company_id'))
            )['value']
            import pdb; pdb.set_trace()
            if defaults.get('tax_id'):
                defaults['tax_id'] = [[6, 0, defaults['tax_id']]]
            values = dict(defaults, **values)
        return super(sale_order_line, self).create(cr, uid, values, context=context)"""