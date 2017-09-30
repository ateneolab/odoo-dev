# -*- coding: utf-8 -*-

from openerp import models, fields, api
import datetime

import logging
_logger = logging.getLogger(__name__)


class mobilvendor_customer(models.Model):
    _name = 'mobilvendor_read.cron_mobilvendor_read'
    
    name = fields.Char(required=True)
    numberOfUpdates = fields.Integer('Number of updates', help='The number of times the scheduler has run and updated this field')
    lastModified = fields.Char('Last updated time')
    lastStartModified = fields.Char('Before last updated time')
    #beforeLastModified = fields.Datetime('Before Last updated')
    meanTime = fields.Float('Tiempo transcurrido desde la ultima actualizacion', digits=(4,2))
    
    def process_mobilvendor_read_scheduler_queue(self, cr, uid, context=None):
        _logger.info("......El cron: Actualizar informacion que lee Mobilvendor - scheduler corriendo...")
        _logger.info("Start time: %s." % datetime.datetime.now())
        
        lastStartModified = False
        
        #  Update clients      OK | Falta poner las coordenadas para la geolocalizacion
        #  Update Direcciones  Son los clientes
        #  Update Carteras      OK
        #  Update Productos     OK
        #  Update Vendedores    OK
        #  Update Pedidos      
        #  Update Bodegas      OK
        #  Update listas de precios  OK
        #  Update categorías de productos  OK
        #  Update inventarios  OK
        #  Update Precios de productos  OK
        #  Update marcas  
        #  Update familias de productos  
        
        self.update_vendedor(cr, uid, context=context)
        self.update_customers(cr, uid, context=context)
        self.update_bodega(cr, uid, context=context)
        self.update_inventario(cr, uid, context=context)
        self.update_producto(cr, uid, context=context)
        self.update_categoriaproducto(cr, uid, context=context)
        self.update_listaprecio(cr, uid, context=context)
        #self.update_precioarticulo(cr, uid, context=context)
        self.update_cartera(cr, uid, context=context)

        scheduler_line_obj = self.pool.get('mobilvendor_read.cron_mobilvendor_read')
        scheduler_line_ids = self.pool.get('mobilvendor_read.cron_mobilvendor_read').search(cr, uid, [])
        
        if len(scheduler_line_ids):
            for scheduler_line_id in scheduler_line_ids:
                scheduler_line =scheduler_line_obj.browse(cr, uid,scheduler_line_id ,context=context)
                numberOfUpdates = scheduler_line.numberOfUpdates
                _logger.info('line: ' + scheduler_line.name)
                data = {
                    'numberOfUpdates': (numberOfUpdates +1),
                    'lastModified': str(datetime.datetime.now()),
                    'lastStartModified': scheduler_line.lastModified
                }
                scheduler_line_obj.write(cr, uid, scheduler_line_id, data, context=context)
        else:
            data = {
                'numberOfUpdates': 1,
                'lastModified': str(datetime.datetime.now()),
                'name': 'Datos de Interpegsa (tomar nombre de company)',
                #'lastStartModified': lastStartModified
            }
            scheduler_line_obj.create(cr, uid, data, context=context)
        _logger.info("End time: %s." % datetime.datetime.now())

    def update_vendedor(self, cr, uid, context=None):
        _logger.info("....Update Vendedores data into MobilVendor integrator...")
        
        env = self.pool.get('crm.case.section')
        ids = env.search(cr, uid, [])  ## y last modified es menor que las updated
        objs = env.browse(cr, uid, ids, context=context)
        
        mv_env = self.pool.get('mobilvendor_read.vendedor')
        for item in objs:
            members = item.member_ids
            
            for seller in members:
                id_odoo = seller.id
                name = seller.name
                identity_ = seller.partner_id.ced_ruc
                
                if seller.name not in ['Administrator', 'Administrator']:
                    identity_type = seller.partner_id.type_ced_ruc
                    if identity_type == 'cedula':
                        identity_type = 'C'
                    elif identity_type == 'R':
                        identity_type = 'R'
                    else:
                        identity_type = 'P'
                    
                    data = {
                        'name': name,
                        'id_odoo': id_odoo,
                        'identity_': identity_,
                        'identity_type': identity_type,
                        'code': identity_,
                    }
    
                    mv_obj = mv_env.search(cr, uid, [('code', '=', data['code'])])
                    if mv_obj and len(mv_obj):
                        mv_env.write(cr, uid, mv_obj, data, context=context)
                    else:
                        mv_env.create(cr, uid, data, context=context)

    """
    Hay que implementar la eliminación de un cliente, aunque no se una funcionalidad que se use frecuentemente
    """
    def update_customers(self, cr, uid, context=None):
        _logger.info("....Update Customer data into MobilVendor integrator...")
        
        customer_env = self.pool.get('res.partner')
        customer_ids = customer_env.search(cr, uid, [('customer', '=', True)])  ## y last modified es menor que las updated
        customer_objs = customer_env.browse(cr, uid, customer_ids, context=context)
        
        mv_customer_env = self.pool.get('mobilvendor_read.customer')
        mv_address_env = self.pool.get('mobilvendor_read.direccion_cliente')
        for customer in customer_objs:
            name = customer.name
            identity_type = customer.type_ced_ruc
            if identity_type == 'cedula':
                identity_type = 'C'
            elif identity_type == 'R':
                identity_type = 'R'
            else:
                identity_type = 'P'
            
            identity_ = customer.ced_ruc
            
            if customer.parent_id:
                company_name = customer.parent_id.name
            else:
                company_name = customer.name

            price_list_code = customer.property_product_pricelist.id
            #payment_method_code = customer.
            status = '1'
            
            vendedor = customer.user_id.name
            if vendedor == u'Administrator' or vendedor == u'Administrador':
                vendedor = 'Sin vendedor asignado'
                
            code_vendedor = ''
            if vendedor and vendedor != 'Sin vendedor asignado':
                code_ = customer.user_id.id
                code_vendedor_id = self.pool.get('mobilvendor_read.vendedor').browse(cr, uid, [code_], context=context)
                code_vendedor = code_vendedor_id.identity_
            
            email = customer.email
            phone = customer.phone
            celular = customer.mobile
            id_odoo = customer.id
            
            parent_id = customer.parent_id.id or ''
            
            data = {
                'code': identity_,
                'name': customer.name,
                'company_name': company_name,
                'identity_type': identity_type,
                'identity_': identity_,
                'price_list_code': price_list_code,
                'status': status,
                'user_code': code_vendedor or 'Sin vendedor asignado',
                ####'code_vendedor': code_vendedor,
                'id_odoo': id_odoo,
                'latitud': customer.partner_latitude,
                'longitud': customer.partner_longitude,
                'parent_id': parent_id,
                'street': customer.street,
                'street2': customer.street2 or '',
                'email': email or '',
                'telefono': phone or '',
                'celular': celular or '',
                'fax': customer.fax or '',
            }
            
            """dir_data = {
                'code': 'PRINCIPAL',
                'customer_code': data['code'],
                'customer_id': data['id_odoo'],
                'street': customer.street or '',
                'street2': customer.street2 or '',
                'email': email or '',
                'telefono': phone or '',
                'celular': celular or '',
                'fax': customer.fax or '',
                'user_code': data['code_vendedor']
            }"""
            
            mv_customer_obj = mv_customer_env.search(cr, uid, [('id_odoo', '=', id_odoo)])
            if mv_customer_obj and len(mv_customer_obj):
                mv_customer_env.write(cr, uid, mv_customer_obj, data, context=context)
                
                """mv_address_obj = mv_address_env.search(cr, uid, [('customer_code', '=', dir_data['customer_code'])])
                
                if mv_address_obj and len(mv_address_obj):
                    mv_address_env.write(cr, uid, mv_address_obj, dir_data, context=context)
                else:
                    mv_address_env.create(cr, uid, dir_data, context=context)"""
            else:
                mv_customer_env.create(cr, uid, data, context=context)
                """mv_address_env.create(cr, uid, dir_data, context=context)"""


    def update_inventario(self, cr, uid, context=None):
        _logger.info("....Update Inventarios data into MobilVendor integrator...")
        
        env = self.pool.get('stock.quant')
        ids = env.search(cr, uid, [])  ## y last modified es menor que las updated
        objs = env.browse(cr, uid, ids, context=context)
        
        mv_env = self.pool.get('mobilvendor_read.inventario')
        for quant in objs:
            article_code = quant.product_id.product_tmpl_id.id
            storage_code = quant.location_id.id
            stock = quant.qty
            
            if quant.location_id.usage in ['internal']:
                data = {
                    'article_code': article_code,
                    'storage_code': storage_code,
                    'stock': stock
                }
                
                mv_obj = mv_env.search(cr, uid, [('article_code', '=', article_code), ('storage_code', '=', storage_code)])
                if mv_obj and len(mv_obj):
                    mv_env.write(cr, uid, mv_obj, data, context=context)
                else:
                    mv_env.create(cr, uid, data, context=context)

    def update_bodega(self, cr, uid, context=None):
        _logger.info("....Update Bodega data into MobilVendor integrator...")
        
        env = self.pool.get('stock.warehouse')
        ids = env.search(cr, uid, [])  ## y last modified es menor que las updated
        objs = env.browse(cr, uid, ids, context=context)
        
        mv_env = self.pool.get('mobilvendor_read.bodega')
        for bodega in objs:
            code = bodega.id
            description = bodega.name
            
            data = {
                'code': code,
                'description': description
            }
            
            mv_obj = mv_env.search(cr, uid, [('code', '=', code)])
            if mv_obj and len(mv_obj):
                mv_env.write(cr, uid, mv_obj, data, context=context)
            else:
                mv_env.create(cr, uid, data, context=context)
                
                
    def update_producto(self, cr, uid, context=None):
        _logger.info("....Update Producto data into MobilVendor integrator...")
        
        env = self.pool.get('product.template')
        ids = env.search(cr, uid, [('type', '=', 'product')])
        objs = env.browse(cr, uid, ids, context=context)
        
        mv_env = self.pool.get('mobilvendor_read.producto')
        
        for prod in objs:
            mv_obj = mv_env.search(cr, uid, [('product_tmpl_id', '=', prod.id)])
            data = {'product_tmpl_id': prod.id}
            
            if mv_obj and len(mv_obj):
                mv_env.write(cr, uid, mv_obj, data, context=context)
            else:
                mv_env.create(cr, uid, data, context=context)

            """code = prod.id
            description = prod.name
            barcode = prod.ean13 or prod.default_code
            category_code = prod.categ_id.id
            has_iva = '1' if prod.taxes_id else '0'
            status = 'Activo' if prod.active else 'Inactivo' 
            sale_price = prod.list_price
            
            data = {
                'code': code,
                'description': description,
                'barcode': barcode,
                'category_code': category_code,
                'has_iva': has_iva,
                'status': status,
                'sale_price': sale_price
            }
            
            mv_obj = mv_env.search(cr, uid, [('code', '=', code)])
            if mv_obj and len(mv_obj):
                mv_env.write(cr, uid, mv_obj, data, context=context)
            else:
                mv_env.create(cr, uid, data, context=context)"""
                
                
    def update_categoriaproducto(self, cr, uid, context=None):
        _logger.info("....Update Categoria Producto data into MobilVendor integrator...")
        
        env = self.pool.get('product.category')
        ids = env.search(cr, uid, [])  ## y last modified es menor que las updated
        objs = env.browse(cr, uid, ids, context=context)
        
        mv_env = self.pool.get('mobilvendor_read.categoriaproducto')
        for item in objs:
            data = {'categ_id': item.id}
            
            """code = item.id
            description = item.name
            parent_category_id = item.parent_id.id if item.parent_id else ''
            
            data = {
                'code': code,
                'description': description,
                'parent_category_id': parent_category_id
            }"""
            
            mv_obj = mv_env.search(cr, uid, [('categ_id', '=', item.id)])
            if mv_obj and len(mv_obj):
                mv_env.write(cr, uid, mv_obj, data, context=context)
            else:
                mv_env.create(cr, uid, data, context=context)
                
       
    def update_listaprecio(self, cr, uid, context=None):
        _logger.info("....Update Lista de precios data into MobilVendor integrator...")
        
        env = self.pool.get('product.pricelist')
        ids = env.search(cr, uid, [('type', '=', 'sale')])  ## y last modified es menor que las updated
        objs = env.browse(cr, uid, ids, context=context)
        
        v_env = self.pool.get('mobilvendor_read.price_list_version')
        i_env = self.pool.get('mobilvendor_read.price_list_item')
        mv_env = self.pool.get('mobilvendor_read.listaprecio')
        
        for pl in objs:
            data = {'pricelist_id': pl.id}

            mv_obj = mv_env.search(cr, uid, [('pricelist_id', '=', data['pricelist_id'])])
            if mv_obj and len(mv_obj):
                mv_env.write(cr, uid, mv_obj, data, context=context)
            else:
                mv_env.create(cr, uid, data, context=context)
                
            for version in pl.version_id:
                v_data = {'version_id': version.id, 'pricelist_code': pl.id}
                
                v_obj = v_env.search(cr, uid, [('version_id', '=', v_data['version_id'])])
                if v_obj and len(v_obj):
                    v_env.write(cr, uid, v_obj, v_data, context=context)
                else:
                    v_env.create(cr, uid, v_data, context=context)
                    
                for item in version.items_id:
                    i_data = {'item_id': item.id, 'version_id': version.id}
                    
                    i_obj = i_env.search(cr, uid, [('item_id', '=', i_data['item_id'])])
                    if i_obj and len(i_obj):
                        i_env.write(cr, uid, i_obj, i_data, context=context)
                    else:
                        i_env.create(cr, uid, i_data, context=context)

    """def update_precioarticulo(self, cr, uid, context=None):
        _logger.info("....Update Precios de productos data into MobilVendor integrator...")
        
        env = self.pool.get('product.pricelist')
        
        ids = env.search(cr, uid, [('type', '=', 'sale')])  ## y last modified es menor que las updated
        objs = env.browse(cr, uid, ids, context=context)
        
        mv_env = self.pool.get('mobilvendor_read.precioarticulo')
        p_env = self.pool.get('product.product')
        for item in objs:  # item = product.pricelist
            if item.version_id:
                version_items = item.version_id.items_id
                
                vi_env = self.pool.get('product.pricelist.item')
                for vi in version_items:  # vi = product.pricelist.item
                    data = {}
                    if vi.categ_id:
                        products_ids = p_env.search(cr, uid, [('categ_id', '=', vi.categ_id.id)])
                        
                        for prod in products_ids:
                            res = env.price_get(cr, uid, [item.id], prod, 1.0)
                            
                            if res:
                                data.update({
                                    'article_code': prod,
                                    'price_list_code': item.id,
                                    'value': res.get(res.keys()[0]),
                                })
                                
                                if 'article_code' in data and 'price_list_code' in data:
                                    mv_obj = mv_env.search(cr, uid, [
                                        ('article_code', '=', data['article_code']), ('price_list_code', '=', data['price_list_code'])])
                                    if mv_obj and len(mv_obj):
                                        mv_env.write(cr, uid, mv_obj, data, context=context)
                                    else:
                                        mv_env.create(cr, uid, data, context=context)
                            
                    if vi.product_id:
                        res = env.price_get(cr, uid, [item.id], vi.product_id.id, 1.0)
                        
                        if res:
                            data.update({
                                'article_code': vi.product_id.id,
                                'price_list_code': item.id,
                                'value': res.get(res.keys()[0]),
                            })
                            
                            if 'article_code' in data and 'price_list_code' in data:
                                mv_obj = mv_env.search(cr, uid, [('article_code', '=', data['article_code']), ('price_list_code', '=', data['price_list_code'])])
                                
                                if mv_obj and len(mv_obj):
                                    mv_env.write(cr, uid, mv_obj, data, context=context)
                                else:
                                    mv_env.create(cr, uid, data, context=context)"""

                    
                    
    def update_cartera(self, cr, uid, context=None):
        _logger.info("....Update Cartera (Cuentas por cobrar) data into MobilVendor integrator...")
        
        env = self.pool.get('account.invoice')
        ids = env.search(cr, uid, [('type', '=', 'out_invoice'), ('amount_total', '>', 0.0)])  ## y last modified es menor que las updated
        objs = env.browse(cr, uid, ids, context=context)
        
        mv_env = self.pool.get('mobilvendor_read.cartera')
        for item in objs:
            data = {
                'code': item.internal_number,
                'customer_code': item.partner_id.ced_ruc,
                'id_odoo': item.id,
                'id_customer': item.partner_id.id,
                'create_date': item.date_invoice,
                ##'expire_date': item.
                'amount': item.amount_total,
                'balance': item.residual,
                'comment': item.comment
            }

            mv_obj = mv_env.search(cr, uid, [('id_odoo', '=', data['id_odoo'])])  # , ('code', '=', data['code'])
            if mv_obj and len(mv_obj):
                mv_env.write(cr, uid, mv_obj, data, context=context)
            else:
                mv_env.create(cr, uid, data, context=context)