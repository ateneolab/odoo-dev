# -*- coding: utf-8 -*-
from openerp import http

# class ShowLotInInvoices(http.Controller):
#     @http.route('/show_lot_in_invoices/show_lot_in_invoices/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/show_lot_in_invoices/show_lot_in_invoices/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('show_lot_in_invoices.listing', {
#             'root': '/show_lot_in_invoices/show_lot_in_invoices',
#             'objects': http.request.env['show_lot_in_invoices.show_lot_in_invoices'].search([]),
#         })

#     @http.route('/show_lot_in_invoices/show_lot_in_invoices/objects/<model("show_lot_in_invoices.show_lot_in_invoices"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('show_lot_in_invoices.object', {
#             'object': obj
#         })