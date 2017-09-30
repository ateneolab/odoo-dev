# -*- coding: utf-8 -*-
from openerp import http

# class ShowPublishedProductPrice(http.Controller):
#     @http.route('/show_published_product_price/show_published_product_price/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/show_published_product_price/show_published_product_price/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('show_published_product_price.listing', {
#             'root': '/show_published_product_price/show_published_product_price',
#             'objects': http.request.env['show_published_product_price.show_published_product_price'].search([]),
#         })

#     @http.route('/show_published_product_price/show_published_product_price/objects/<model("show_published_product_price.show_published_product_price"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('show_published_product_price.object', {
#             'object': obj
#         })