# -*- coding: utf-8 -*-
from openerp import http

# class ForceDefaults(http.Controller):
#     @http.route('/force_defaults/force_defaults/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/force_defaults/force_defaults/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('force_defaults.listing', {
#             'root': '/force_defaults/force_defaults',
#             'objects': http.request.env['force_defaults.force_defaults'].search([]),
#         })

#     @http.route('/force_defaults/force_defaults/objects/<model("force_defaults.force_defaults"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('force_defaults.object', {
#             'object': obj
#         })