# -*- coding: utf-8 -*-
from openerp import http

# class InvoiceDiscountAmount(http.Controller):
#     @http.route('/invoice_discount_amount/invoice_discount_amount/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/invoice_discount_amount/invoice_discount_amount/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('invoice_discount_amount.listing', {
#             'root': '/invoice_discount_amount/invoice_discount_amount',
#             'objects': http.request.env['invoice_discount_amount.invoice_discount_amount'].search([]),
#         })

#     @http.route('/invoice_discount_amount/invoice_discount_amount/objects/<model("invoice_discount_amount.invoice_discount_amount"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('invoice_discount_amount.object', {
#             'object': obj
#         })