# -*- coding: utf-8 -*-
from openerp import http

# class ForceSaleCompany(http.Controller):
#     @http.route('/force_sale_company/force_sale_company/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/force_sale_company/force_sale_company/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('force_sale_company.listing', {
#             'root': '/force_sale_company/force_sale_company',
#             'objects': http.request.env['force_sale_company.force_sale_company'].search([]),
#         })

#     @http.route('/force_sale_company/force_sale_company/objects/<model("force_sale_company.force_sale_company"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('force_sale_company.object', {
#             'object': obj
#         })