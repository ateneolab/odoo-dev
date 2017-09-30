# -*- coding: utf-8 -*-

from openerp import models, fields, api


class mobilvendor_customer(models.Model):
    _name = 'mobilvendor_read.customer'
    
    code = fields.Char('Numero de identificacion')  # Hay que revisar si el RUC es unico o se comparte entre distintos puntos de venta
    name = fields.Char('Nombre')
    company_name = fields.Char('Empresa')
    identity_type = fields.Char('Tipo de identificacion')
    identity_ = fields.Char('Identificacion')
    price_list_code = fields.Char('Lista de precios')  # product.pricelist
    #payment_method_code = fields.Char('Metodo de pago')
    status = fields.Char('Estado')
    ####vendedor = fields.Char('Vendedor')
    ####code_vendedor = fields.Char('Id del usuario comercial en Odoo')
    ####email = fields.Char('Email')
    ####telefono = fields.Char('Telefono')
    ####celular = fields.Char('Celular')
    ####localidad = fields.Char('Localidad')  # city
    id_odoo = fields.Char('Id Odoo')
    ####street1 = fields.Char('Calle 1')
    ####street2 = fields.Char('Calle 2 (Intercepcion)')
    ####user_code = fields.Char('Codigo usuario')  # lo pone mobilvendor
    #contact_name = fields.Char('Nombre contacto')  # no está
    latitud = fields.Float(digits=(4,8), string='Latitud')
    longitud = fields.Float(digits=(4,8), string='Longitud')
    parent_id = fields.Char('Empresa padre')
    
    email = fields.Char('Email')
    telefono = fields.Char('Telefono')
    celular = fields.Char('Celular')
    fax = fields.Char('Fax')
    ####code = fields.Char('Numero identificacion cliente')
    ####customer_code = fields.Char('Codigo cliente')
    ####customer_id = fields.Char('Id cliente en Odoo')
    street = fields.Char('Calle principal')
    street2 = fields.Char('Calle secundaria (Intercepcion)')
    user_code = fields.Char('Codigo usuario - vendedor asignado')
    
    
"""class direccion_cliente(models.Model):
    _name = 'mobilvendor_read.direccion_cliente'
    
    code = fields.Char('Numero identificacion cliente')
    customer_code = fields.Char('Codigo cliente')
    customer_id = fields.Char('Id cliente en Odoo')
    street1 = fields.Char('Calle 1')
    street2 = fields.Char('Calle 2 (Intercepcion)')
    ###block = fields.Char('Nomenclatura')
    user_code = fields.Char('Codigo usuario - vendedor asignado')
    ###week = fields.Char('Semana')
    ###day = fields.Char('Dia')
    ###contact_name = fields.Char('Nombre contacto')    
    ###name = fields.Char('Nombre descriptivo')
    email = fields.Char('Email')
    telefono = fields.Char('Telefono')
    celular = fields.Char('Celular')
    fax = fields.Char('Fax')"""

    
class bodega(models.Model):
    _name = 'mobilvendor_read.bodega'
    
    code = fields.Char('Codigo - Id Odoo')
    description = fields.Char('Descripcion - Nombre en Odoo')
    #id_odoo = fields.Char('Id Odoo')
    

"""class categoriaproducto(models.Model):
    _name = 'mobilvendor_read.categoriaproducto'
    
    code = fields.Char('Id Odoo')
    description = fields.Char('Descripcion - Nombre en Odoo')"""
    #id_odoo = fields.Char('Id Odoo')


class inventario(models.Model):
    _name = 'mobilvendor_read.inventario'
    
    article_code = fields.Char('Id del producto en Odoo')
    storage_code = fields.Char('Id de la bodega en Odoo')
    stock = fields.Float(digits=(20,2), string='Cantidad disponible')
    
    
class producto(models.Model):
    _name = 'mobilvendor_read.producto'

    product_tmpl_id = fields.Many2one('product.template')
    code = fields.Char(string='Id Odoo')
    name = fields.Char(string='Nombre')
    description = fields.Char(string='Descripcion')
    barcode = fields.Char(string='Barcode')
    #family_code = fields.Char('Id Odoo')  # no esta
    #brand_code = fields.Char('Id Odoo')  # no esta
    category_code = fields.Char(string='Categoria')
    #unit_code = fields.Char('')
    has_iva = fields.Char(string='Con IVA')  # si taxes_id tiene valor entonces es 1
    status = fields.Char(string='Estado')  # active
    sale_price = fields.Char(string='Precio de venta')  # list_price
    cost_price = fields.Char(string='Precio de coste')  # standard_price
    
    @api.model
    def create(self, vals):
        if 'product_tmpl_id' in vals:
            product_tmpl_id = self.env['product.template'].browse(vals.get('product_tmpl_id'))
            
            if product_tmpl_id:
                vals.update({
                    'code': product_tmpl_id.id,
                    'name': product_tmpl_id.name,
                    'description': product_tmpl_id.type,
                    'barcode': product_tmpl_id.ean13 or product_tmpl_id.default_code,
                    'status': '1' if product_tmpl_id.active else '0',
                    'sale_price': product_tmpl_id.list_price,
                    'sale_price': product_tmpl_id.standard_price,
                    'has_iva': '1' if product_tmpl_id.taxes_id else '0',
                    'category_code': product_tmpl_id.categ_id.id
                })
                
        return super(producto, self).create(vals)
        
    @api.multi
    def write(self, vals):
        if 'product_tmpl_id' in vals:
            product_tmpl_id = self.env['product.template'].browse(vals.get('product_tmpl_id'))
            
            if product_tmpl_id:
                vals.update({
                    'code': product_tmpl_id.id,
                    'name': product_tmpl_id.name,
                    'description': product_tmpl_id.type,
                    'barcode': product_tmpl_id.ean13 or product_tmpl_id.default_code,
                    'status': '1' if product_tmpl_id.active else '0',
                    'sale_price': product_tmpl_id.list_price,
                    'sale_price': product_tmpl_id.standard_price,
                    'has_iva': '1' if product_tmpl_id.taxes_id else '0',
                    'category_code': product_tmpl_id.categ_id.id
                })
                
        return super(producto, self).write(vals)
    
    
class categoriaproducto(models.Model):
    _name = 'mobilvendor_read.categoriaproducto'

    categ_id = fields.Many2one('product.category')
    code = fields.Char('Codigo')
    description = fields.Char('Descripcion')
    parent_category_id = fields.Char('Id categoria padre en Odoo (code categoria padre)')
    name = fields.Char('Nombre')
    
    @api.model
    def create(self, vals):
        if 'categ_id' in vals:
            categ_id = self.env['product.category'].browse(vals.get('categ_id'))

            if categ_id:
                vals.update({
                    'code': categ_id.id,
                    'description': categ_id.type,
                    'name': categ_id.name,
                    'categ_id': categ_id.id,
                })
                
                if categ_id.parent_id:
                    vals.update({
                        'parent_category_id': categ_id.parent_id.id
                    })
                
        return super(categoriaproducto, self).create(vals)
        
    @api.multi
    def write(self, vals):
        if 'categ_id' in vals:
            categ_id = self.env['product.category'].browse(vals.get('categ_id'))
            
            if categ_id:
                vals.update({
                    'code': categ_id.id,
                    'description': categ_id.type,
                    'name': categ_id.name,
                    'categ_id': categ_id.id,
                })
                
                if categ_id.parent_id:
                    vals.update({
                        'parent_category_id': categ_id.parent_id.id
                    })
                
        return super(categoriaproducto, self).write(vals)
    
    
class listaprecio(models.Model):
    _name = 'mobilvendor_read.listaprecio'

    pricelist_id = fields.Many2one('product.pricelist')
    code = fields.Char(string='Codigo')
    description = fields.Char(string='Descripcion')
    
    @api.model
    def create(self, vals):
        if 'pricelist_id' in vals:
            pricelist_id = self.env['product.pricelist'].browse(vals.get('pricelist_id'))
            
            if pricelist_id:
                vals.update({
                    'code': pricelist_id.id,
                    'description': pricelist_id.type,
                })
                
        return super(listaprecio, self).create(vals)
        
    @api.multi
    def write(self, vals):
        if 'pricelist_id' in vals:
            pricelist_id = self.env['product.pricelist'].browse(vals.get('pricelist_id'))
            
            if pricelist_id:
                vals.update({
                    'code': pricelist_id.id,
                    'description': pricelist_id.type,
                })
                
        return super(listaprecio, self).write(vals)
    
    
class precioarticulo(models.Model):
    _name = 'mobilvendor_read.precioarticulo'
    
    article_code = fields.Char('Id Producto en Odoo')
    price_list_code = fields.Char('Id Lista de precios en Odoo')
    version_id = fields.Char('Id Pricelist version en Odoo')
    value = fields.Float(digits=(10, 2), string='Precio producto')
    

class vendedor(models.Model):
    _name = 'mobilvendor_read.vendedor'
    
    code = fields.Char('identity_')
    id_odoo = fields.Char('Id en Odoo')
    name = fields.Char('Nombre en Odoo')
    identity_type = fields.Char('Tipo de identificacion')
    identity_ = fields.Char('Cedula o RUC')
    
    
class cartera(models.Model):
    _name = 'mobilvendor_read.cartera'
    
    code = fields.Char('Codigo secuencial de la factura de cliente')
    customer_code = fields.Char('Codigo de cliente')
    id_odoo = fields.Char('Id de la factura en Odoo')
    id_customer = fields.Char('Id del cliente en Odoo')
    create_date = fields.Char('Fecha factura')
    #expire_date = fields.Char('Fecha expiracion')
    amount = fields.Float(digits=(10, 2), string='Monto')
    balance = fields.Float(digits=(10, 2), string='Balance')
    comment = fields.Char('Comentarios')

"""class usuario(models.Model):
    _name = 'mobilvendor_read.usuario'
    
    code = fields.Char('Codigo MobilVendor')
    customer_code = fields.Char('Codigo Cliente MobilVendor')
    customer_id = fields.Char('Id Cliente Odoo')
    create_date = fields.Char('Fecha factura')
    expire_date = fields.Char('Fecha expiracion')
    amount = fields.Float(digits=(10,2), string='Monto')
    balance = fields.Float(digits=(10,2), string='Balance')
    comment = fields.Char('Comentarios')"""
    
    
class price_list_version(models.Model):
    _name = 'mobilvendor_read.price_list_version'

    version_id = fields.Many2one('product.pricelist.version')
    code = fields.Char(string='Codigo')
    date_start = fields.Char(string='Fecha de inicio')
    date_end = fields.Char(string='Fecha fin')
    name = fields.Char(string='Nombre')
    pricelist_code = fields.Char(string='Nombre')
    
    @api.model
    def create(self, vals):
        if 'version_id' in vals:
            version_id = self.env['product.pricelist.version'].browse(vals.get('version_id'))
            
            if version_id:
                vals.update({
                    'code': version_id.id,
                    'date_start': version_id.date_start,
                    'date_end': version_id.date_end,
                    'name': version_id.name,
                })
                
        return super(price_list_version, self).create(vals)
        
    @api.multi
    def write(self, vals):
        if 'version_id' in vals:
            version_id = self.env['product.pricelist.version'].browse(vals.get('version_id'))
            
            if version_id:
                vals.update({
                    'code': version_id.id,
                    'date_start': version_id.date_start,
                    'date_end': version_id.date_end,
                    'name': version_id.name,
                })
                
        return super(price_list_version, self).write(vals)
    

class price_list_item(models.Model):
    _name = 'mobilvendor_read.price_list_item'

    item_id = fields.Many2one('product.pricelist.item')
    code = fields.Char(string='Codigo')
    product_tmpl_id = fields.Char(string='Producto')
    category_id = fields.Char(string='Categoria')
    min_quantity = fields.Char(string='Cantidad minima')
    sequence = fields.Char(string='Prioridad')
    base = fields.Char(string='Basado en')  # [1-> Precio publico, 2-> Precio de coste, -1-> Otra tarifa (base_price_list_id)]
    base_price_list_id = fields.Char(string='Tarifa de referencia')
    price_discount = fields.Char(string='Descuento')
    price_surcharge = fields.Char(string='Sobrecargo de precio')
    version_id = fields.Char(string='Version tarifa')

    @api.model
    def create(self, vals):
        if 'item_id' in vals:
            item_id = self.env['product.pricelist.item'].browse(vals.get('item_id'))
            
            if item_id:
                vals.update({
                    'code': item_id.id,
                    'min_quantity': item_id.min_quantity,
                    'sequence': item_id.sequence,
                    'base': item_id.base,
                    'price_discount': item_id.price_discount,
                    'price_surcharge': item_id.price_surcharge,
                })
                
                if item_id.product_tmpl_id:
                    vals.update({'product_tmpl_id': item_id.product_tmpl_id.id})
                    
                if item_id.categ_id:
                    vals.update({'category_id': item_id.categ_id.id})
                    
                if item_id.base_pricelist_id:
                    vals.update({'base_price_list_id': item_id.base_pricelist_id.id})
                
        return super(price_list_item, self).create(vals)
        
    @api.multi
    def write(self, vals):
        if 'item_id' in vals:
            item_id = self.env['product.pricelist.item'].browse(vals.get('item_id'))
            
            if item_id:
                vals.update({
                    'code': item_id.id,
                    'min_quantity': item_id.min_quantity,
                    'sequence': item_id.sequence,
                    'base': item_id.base,
                    'price_discount': item_id.price_discount,
                    'price_surcharge': item_id.price_surcharge,
                })
                
                if item_id.product_tmpl_id:
                    vals.update({'product_tmpl_id': item_id.product_tmpl_id.id})
                    
                if item_id.categ_id:
                    vals.update({'category_id': item_id.categ_id.id})
                    
                if item_id.base_pricelist_id:
                    vals.update({'base_price_list_id': item_id.base_pricelist_id.id})
                
        return super(price_list_item, self).write(vals)