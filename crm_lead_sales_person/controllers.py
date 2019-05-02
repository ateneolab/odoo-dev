# -*- coding: utf-8 -*-
from openerp import http

# class CrmLeadSalesPerson(http.Controller):
#     @http.route('/crm_lead_sales_person/crm_lead_sales_person/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/crm_lead_sales_person/crm_lead_sales_person/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('crm_lead_sales_person.listing', {
#             'root': '/crm_lead_sales_person/crm_lead_sales_person',
#             'objects': http.request.env['crm_lead_sales_person.crm_lead_sales_person'].search([]),
#         })

#     @http.route('/crm_lead_sales_person/crm_lead_sales_person/objects/<model("crm_lead_sales_person.crm_lead_sales_person"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('crm_lead_sales_person.object', {
#             'object': obj
#         })