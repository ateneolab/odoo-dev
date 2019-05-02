# -*- coding: utf-8 -*-
from openerp import http

# class MailOutgoingServer(http.Controller):
#     @http.route('/mail_outgoing_server/mail_outgoing_server/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/mail_outgoing_server/mail_outgoing_server/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('mail_outgoing_server.listing', {
#             'root': '/mail_outgoing_server/mail_outgoing_server',
#             'objects': http.request.env['mail_outgoing_server.mail_outgoing_server'].search([]),
#         })

#     @http.route('/mail_outgoing_server/mail_outgoing_server/objects/<model("mail_outgoing_server.mail_outgoing_server"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('mail_outgoing_server.object', {
#             'object': obj
#         })