# -*- coding: utf-8 -*-
from openerp import http

# class FixDiscountType(http.Controller):
#     @http.route('/fix_discount_type/fix_discount_type/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/fix_discount_type/fix_discount_type/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('fix_discount_type.listing', {
#             'root': '/fix_discount_type/fix_discount_type',
#             'objects': http.request.env['fix_discount_type.fix_discount_type'].search([]),
#         })

#     @http.route('/fix_discount_type/fix_discount_type/objects/<model("fix_discount_type.fix_discount_type"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('fix_discount_type.object', {
#             'object': obj
#         })