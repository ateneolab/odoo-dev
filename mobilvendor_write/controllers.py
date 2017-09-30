# -*- coding: utf-8 -*-
from openerp import http

# class MobilvendorWrite(http.Controller):
#     @http.route('/mobilvendor_write/mobilvendor_write/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mobilvendor_write/mobilvendor_write/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mobilvendor_write.listing', {
#             'root': '/mobilvendor_write/mobilvendor_write',
#             'objects': http.request.env['mobilvendor_write.mobilvendor_write'].search([]),
#         })

#     @http.route('/mobilvendor_write/mobilvendor_write/objects/<model("mobilvendor_write.mobilvendor_write"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mobilvendor_write.object', {
#             'object': obj
#         })