# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError


class Contract(models.Model):
    _name = 'education_contract.contract'
    _inherit = 'education_contract.contract'

    verification_id = fields.Many2one('education_contract.verification', 'contract_id')

    @api.multi
    def to_assigned(self):
        filled = self.validate_filled()

        if not filled:
            raise ValidationError("Debe completar todos los datos del contrato para cambiar a estado 'Asignado'.")
        else:
            active_plan_id = self.plan_id.copy({
                'payment_term_ids': None,
                'amount_pay': self.plan_id.residual,
                'plan_active': True,
                'start_date': datetime.today(),
                'contract_id': None
            })

            active_plan_id.reschedule()

            self.env['collection_plan.collection_plan'].create({
                'active_plan_id': active_plan_id.id,
                'start_date': active_plan_id.start_date,
                'contract_id': self.id,
            })

            self.write({'state': 'asigned'})
