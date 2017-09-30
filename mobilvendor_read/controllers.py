# -*- coding: utf-8 -*-
from openerp import http

# class MobilvendorRead(http.Controller):
#     @http.route('/mobilvendor_read/mobilvendor_read/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mobilvendor_read/mobilvendor_read/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mobilvendor_read.listing', {
#             'root': '/mobilvendor_read/mobilvendor_read',
#             'objects': http.request.env['mobilvendor_read.mobilvendor_read'].search([]),
#         })

#     @http.route('/mobilvendor_read/mobilvendor_read/objects/<model("mobilvendor_read.mobilvendor_read"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mobilvendor_read.object', {
#             'object': obj
#         })