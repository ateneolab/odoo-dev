# -*- coding: iso-8859-1 -*-

from datetime import datetime

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class Contract(models.Model):
    _name = 'education_contract.contract'
    _inherit = 'education_contract.contract'

    verification_id = fields.Many2one('education_contract.verification', 'contract_id')
    roll_number_ids = fields.One2many('op.roll.number', 'contract_id', u'Matrículas')
    date_booking_schedule = fields.Date(u'Fecha de separación de horario')
    start_date = fields.Date(u'Fecha de inicio de clases')

    @api.one
    @api.depends('beneficiary_ids_2')
    def enroll(self):
        program_ids = []
        for ben in self.beneficiary_ids_2:
            program_ids.append(ben.program_ids)
        for prog in program_ids:
            roll_number = self.env['op.roll.number'].search(
                [
                    ('course_id', '=', prog.course_id.id),
                    ('division_id', '=', prog.division_id.id),
                    ('student_id', '=', prog.beneficiary_id.student_id.id),
                    ('standard_id', '=', prog.standard_id.id),
                    ('batch_id', '=', prog.batch_id.id),
                    ('beneficiary_id', '=', prog.beneficiary_id.id),
                    ('contract_id', '=', self.id),
                ]
            )
            if not roll_number:
                data = {
                    'course_id': prog.course_id.id,
                    'division_id': prog.division_id.id,
                    'student_id': prog.beneficiary_id.student_id.id,
                    'standard_id': prog.standard_id.id,
                    'batch_id': prog.batch_id.id,
                    'roll_number': '1',
                    'beneficiary_id': prog.beneficiary_id.id,
                    'contract_id': self.id,
                    'state': 'inactive'
                }
                if self.date_booking_schedule:
                    data.update({'schedule_reservation_date': self.date_booking_schedule})
                else:
                    data.update({'schedule_reservation_date': datetime.today()})
                if self.start_date:
                    data.update({'start_date': self.start_date})
                self.env['op.roll.number'].create(data)

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

            # try:
            #     beneficiary_ids = self.copy_beneficiaries()
            # except Exception as e:
            #     raise e

            verification_id = self.env['education_contract.verification'].create(plan_data)
            # verification_id.write({'beneficiary_ids': self.beneficiary_ids_2})

            verification_id.write({'beneficiary_ids': [(6, 0, self.beneficiary_ids_2.ids)]})

            self.write({
                'state': 'asigned',
                'verification_id': verification_id.id,
            })


class Beneficiary(models.Model):
    _name = 'education_contract.beneficiary'
    _inherit = 'education_contract.beneficiary'

    verification_id = fields.Many2one('education_contract.verification', string=_('Contract verification'))


class PaymentTerm(models.Model):
    _name = 'education_contract.payment_term'
    _inherit = 'education_contract.payment_term'

    tax_ids = fields.Many2many('account.tax', string=_('Taxes'))
    taxes_included = fields.Boolean(_(u'Taxes included'))

# class Plan(models.Model):
#     _name = 'education_contract.plan'
#     _inherit = 'education_contract.plan'
#
#     start_date = fields.Date('Fecha de inicio')

# class Plan(models.Model):
#     _name = 'education_contract.plan'
#     _inherit = 'education_contract.plan'
#
#     start_date = fields.Date('Fecha de inicio')
