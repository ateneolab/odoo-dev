# -*- coding: utf-8 -*-

from openerp import models, fields, api


class pedido(models.Model):
    _name = 'mobilvendor_write.order'
    
    code = fields.Char('Codigo de creacion (Mobilvendor)')  # debe existir el campo en Odoo
    partner_id = fields.Char('Id del Cliente en Odoo') # Codigo del cliente (Numero de Identificacion del cliente)
    partner_code = fields.Char('Codigo de cliente en Mobilvendor') # Codigo del cliente (Numero de Identificacion del cliente)
    partner_invoice_code = fields.Char('Direccion factura') # Codigo del cliente-direccion
    partner_shipping_id = fields.Char('Direccion de entrega')  # Codigo del cliente-direccion
    date_order = fields.Char('Fecha pedido')
    pricelist_id = fields.Char('Codigo de Tarifa')
    wh = fields.Char('Codigo de Bodega')
    sales_people = fields.Char('Codigo de Vendedor')  # Id del usuario en Odoo, Mobilvendor ya lo tiene
    status = fields.Char('Estado')
    amount_untaxed = fields.Float(digits=(6,4), string='Subtotal')
    taxes = fields.Float(digits=(6,4), string='Impuestos')
    amount_total = fields.Float(digits=(6,4), string='Total')
    peso = fields.Float(digits=(6,4), string='Peso')
    volume = fields.Float(digits=(6,4), string='Volumen')
    user_code = fields.Char('Codigo usuario - vendedor asignado')
    order_id = fields.Char('Id del pedido en Odoo')
    read = fields.Boolean('Actualizado en Odoo')
    
    
class lineapedido(models.Model):
    _name = 'mobilvendor_write.order_line'
    
    order_code = fields.Char('Codigo del pedido')  # debe existir el campo en Odoo
    order_id = fields.Char('Id del pedido en Odoo')
    product_code = fields.Char('Codigo del Producto')
    quantity = fields.Float(digits=(10, 4), string='Cantidad')
    price_unit = fields.Float(digits=(10, 4), string='Precio unidad')
    iva = fields.Boolean('Con iva')
    porcentaje_iva = fields.Float(digits=(4,4), string='Porciento IVA')
    shipping_date = fields.Char('Tiempo de entrega')
    price_subtotal = fields.Float(digits=(10, 4), string='Subtotal')
    discount = fields.Float(digits=(4,4), string='Subtotal')
    ice = fields.Boolean('Con ICE')
    porcentaje_ice = fields.Float(digits=(4, 4), string='Porciento ICE')
    read = fields.Boolean('Actualizado en Odoo')
    

class mobilvendor_customer(models.Model):
    _name = 'mobilvendor_write.customer'
    
    code = fields.Char('Numero de identificacion')  # Hay que revisar si el RUC es unico o se comparte entre distintos puntos de venta
    name = fields.Char('Nombre')
    company_name = fields.Char('Empresa')
    identity_type = fields.Char('Tipo de identificacion')
    identity_ = fields.Char('Identificacion')
    price_list_code = fields.Char('Lista de precios')  # product.pricelist
    status = fields.Char('Estado')
    id_odoo = fields.Char('Id Odoo')
    latitud = fields.Float(digits=(4,8), string='Latitud')
    longitud = fields.Float(digits=(4,8), string='Longitud')
    parent_id = fields.Char('Empresa padre')
    email = fields.Char('Email')
    telefono = fields.Char('Telefono')
    celular = fields.Char('Celular')
    fax = fields.Char('Fax')
    street1 = fields.Char('Calle 1')
    street2 = fields.Char('Calle 2 (Intercepcion)')
    user_code = fields.Char('Codigo usuario - vendedor asignado')
    read = fields.Boolean('Actualizado en Odoo')
    

class cartera(models.Model):
    _name = 'mobilvendor_write.cartera'
    
    code = fields.Char('Codigo secuencial de la factura de cliente')  # Hay que acordar como establecerlo desde mobilvendor
    customer_code = fields.Char('Codigo de cliente')
    id_odoo = fields.Char('Id de la factura en Odoo')
    id_customer = fields.Char('Id del cliente en Odoo')
    create_date = fields.Char('Fecha factura')
    amount = fields.Float(digits=(10, 2), string='Monto')
    balance = fields.Float(digits=(10, 2), string='Balance')
    comment = fields.Char('Comentarios')
    read = fields.Boolean('Actualizado en Odoo')
    
"""
class payment(models.Model):
    _name = 'mobilvendor_write.payment'
    
    code = fields.Char('Codigo del pago')  # Hay que acordar como establecerlo desde mobilvendor
    customer_code = fields.Char('Codigo del cliente')
    invoice_code = fields.Char('Codigo de la factura')
    id_invoice_odoo = fields.Char('Id de la factura en Odoo')
    id_customer = fields.Char('Id del cliente en Odoo')
    create_date = fields.Char('Fecha factura')
    amount = fields.Float(digits=(10, 5), string='Fecha factura')
    payment_method = fields.Char('Metodo de pago (Banco, Efectivo)')
    read = fields.Boolean('Actualizado en Odoo')
""" 