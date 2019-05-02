# -*- coding: utf-8 -*-
from openerp import http

# class SurveyResend(http.Controller):
#     @http.route('/survey_resend/survey_resend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/survey_resend/survey_resend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('survey_resend.listing', {
#             'root': '/survey_resend/survey_resend',
#             'objects': http.request.env['survey_resend.survey_resend'].search([]),
#         })

#     @http.route('/survey_resend/survey_resend/objects/<model("survey_resend.survey_resend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('survey_resend.object', {
#             'object': obj
#         })