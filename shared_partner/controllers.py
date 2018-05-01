# -*- coding: utf-8 -*-
from openerp import http

# class SharedPartner(http.Controller):
#     @http.route('/shared_partner/shared_partner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/shared_partner/shared_partner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('shared_partner.listing', {
#             'root': '/shared_partner/shared_partner',
#             'objects': http.request.env['shared_partner.shared_partner'].search([]),
#         })

#     @http.route('/shared_partner/shared_partner/objects/<model("shared_partner.shared_partner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('shared_partner.object', {
#             'object': obj
#         })