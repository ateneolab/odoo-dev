# -*- coding: utf-8 -*-
from openerp import http

# class EducationContract(http.Controller):
#     @http.route('/education_contract/education_contract/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/education_contract/education_contract/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('education_contract.listing', {
#             'root': '/education_contract/education_contract',
#             'objects': http.request.env['education_contract.education_contract'].search([]),
#         })

#     @http.route('/education_contract/education_contract/objects/<model("education_contract.education_contract"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('education_contract.object', {
#             'object': obj
#         })