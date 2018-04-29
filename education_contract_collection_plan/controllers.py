# -*- coding: utf-8 -*-
from openerp import http

# class EducationContractCollectionPlan(http.Controller):
#     @http.route('/education_contract_collection_plan/education_contract_collection_plan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/education_contract_collection_plan/education_contract_collection_plan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('education_contract_collection_plan.listing', {
#             'root': '/education_contract_collection_plan/education_contract_collection_plan',
#             'objects': http.request.env['education_contract_collection_plan.education_contract_collection_plan'].search([]),
#         })

#     @http.route('/education_contract_collection_plan/education_contract_collection_plan/objects/<model("education_contract_collection_plan.education_contract_collection_plan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('education_contract_collection_plan.object', {
#             'object': obj
#         })