# -*- coding: utf-8 -*-
from openerp import http

# class EcOperatingUnit(http.Controller):
#     @http.route('/ec_operating_unit/ec_operating_unit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/ec_operating_unit/ec_operating_unit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('ec_operating_unit.listing', {
#             'root': '/ec_operating_unit/ec_operating_unit',
#             'objects': http.request.env['ec_operating_unit.ec_operating_unit'].search([]),
#         })

#     @http.route('/ec_operating_unit/ec_operating_unit/objects/<model("ec_operating_unit.ec_operating_unit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('ec_operating_unit.object', {
#             'object': obj
#         })