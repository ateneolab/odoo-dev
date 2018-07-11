# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
from dateutil import parser


class sale_order(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    education_contract_id = fields.Many2one('education_contract.contract', string='Contrato de estudios')
    generate_contract = fields.Boolean(_('Generate contract'), default=True)

    def action_button_confirm(self, cr, uid, ids, context=None):
        res = super(sale_order, self).action_button_confirm(cr, uid, ids, context=context)

        sale_o = self.pool.get('sale.order').browse(cr, uid, ids, context=context)

        if res and sale_o and sale_o.generate_contract:
            contract_id = self.generate_education_contract(cr, uid, ids, context=context)

            if contract_id:
                self.pool.get('sale.order').write(cr, uid, ids, {'education_contract_id': contract_id})
                self.pool.get('education_contract.contract').write(cr, uid, [contract_id],
                                                                   {'campus_id':
                                                                        sale_o.operating_unit_id.id}, context=context)

        return res

    def generate_education_contract(self, cr, uid, ids, context=None):

        contract_id = self.pool.get('education_contract.contract').create(cr, uid, {'sale_order_id': ids},
                                                                          context=context)
        return contract_id
