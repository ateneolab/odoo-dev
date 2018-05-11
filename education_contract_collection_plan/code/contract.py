# -*- coding: iso-8859-1 -*-

from datetime import datetime

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class Contract(models.Model):
    _name = 'education_contract.contract'
    _inherit = 'education_contract.contract'

    verification_id = fields.Many2one('education_contract.verification', 'contract_id')

    @api.multi
    def copy_active_plan(self):
        self.ensure_one()

        active_plan_id = self.plan_id.copy({
            'payment_term_ids': None,
            'amount_pay': self.plan_id.residual,
            'plan_active': True,
            'start_date': datetime.today(),
            'contract_id': None
        })

        active_plan_id.reschedule()

        plan_data = {
            'plan_id': active_plan_id.id,
            'start_date': active_plan_id.start_date,
            'contract_id': self.id,
        }

        return plan_data

    @api.multi
    def copy_beneficiaries(self):
        self.ensure_one()
        import pdb
        pdb.set_trace()

        b_list = []

        try:
            for ben in self.beneficiary_ids_2:
                b_list.append((4, ben.id))
        except Exception as e:
            raise e

        return {
            'beneficiary_ids': b_list
        }

    @api.multi
    def to_assigned(self):
        self.ensure_one()

        filled = self.validate_filled()

        if not filled:
            raise ValidationError("Debe completar todos los datos del contrato para cambiar a estado 'Asignado'.")
        else:
            try:
                # verification_id = self.copy_active_plan()
                plan_data = self.copy_active_plan()
            except Exception as e:
                raise e

            import pdb
            pdb.set_trace()

            # try:
            #     beneficiary_ids = self.copy_beneficiaries()
            # except Exception as e:
            #     raise e

            verification_id = self.env['education_contract.verification'].create(plan_data)
            verification_id.write({
                'beneficiary_ids': self.beneficiary_ids_2
            })

            self.write({
                'state': 'asigned',
                'verification_id': verification_id.id,
            })


class Beneficiary(models.Model):
    _name = 'education_contract.beneficiary'
    _inherit = 'education_contract.beneficiary'

    verification_id = fields.Many2one('education_contract.verification', string=_('Contract verification'))
