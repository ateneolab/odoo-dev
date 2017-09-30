# -*- coding: utf-8 -*-
from openerp import http

# class L10nEcAlRetention(http.Controller):
#     @http.route('/l10n_ec_al_retention/l10n_ec_al_retention/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/l10n_ec_al_retention/l10n_ec_al_retention/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('l10n_ec_al_retention.listing', {
#             'root': '/l10n_ec_al_retention/l10n_ec_al_retention',
#             'objects': http.request.env['l10n_ec_al_retention.l10n_ec_al_retention'].search([]),
#         })

#     @http.route('/l10n_ec_al_retention/l10n_ec_al_retention/objects/<model("l10n_ec_al_retention.l10n_ec_al_retention"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('l10n_ec_al_retention.object', {
#             'object': obj
#         })