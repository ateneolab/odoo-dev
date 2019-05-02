# -*- coding: utf-8 -*-
from openerp import http

# class CollectionPlan(http.Controller):
#     @http.route('/collection_plan/collection_plan/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/collection_plan/collection_plan/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('collection_plan.listing', {
#             'root': '/collection_plan/collection_plan',
#             'objects': http.request.env['collection_plan.collection_plan'].search([]),
#         })

#     @http.route('/collection_plan/collection_plan/objects/<model("collection_plan.collection_plan"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('collection_plan.object', {
#             'object': obj
#         })