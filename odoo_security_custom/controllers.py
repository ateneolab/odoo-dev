# -*- coding: utf-8 -*-
from openerp import http

# class OdooSecurityCustom(http.Controller):
#     @http.route('/odoo_security_custom/odoo_security_custom/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/odoo_security_custom/odoo_security_custom/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('odoo_security_custom.listing', {
#             'root': '/odoo_security_custom/odoo_security_custom',
#             'objects': http.request.env['odoo_security_custom.odoo_security_custom'].search([]),
#         })

#     @http.route('/odoo_security_custom/odoo_security_custom/objects/<model("odoo_security_custom.odoo_security_custom"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('odoo_security_custom.object', {
#             'object': obj
#         })