# -*- coding: iso-8859-1 -*-

from datetime import datetime

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.exceptions import except_orm

"""class OperatingUnit(models.Model):
    _inherit = 'operating.unit'

    @api.model
    def create(self, vals):
        if vals == {}:
            return False
        res = super(OperatingUnit, self).create(vals)
        return res"""


class Contract(models.Model):
    _name = 'education_contract.contract'
    _inherit = 'education_contract.contract'

    verification_id = fields.Many2one('education_contract.verification', 'contract_id')
    roll_number_ids = fields.One2many('op.roll.number', 'contract_id', u'Matrículas')
    date_booking_schedule = fields.Date(u'Fecha de separación de horario')
    start_date = fields.Date(u'Fecha de inicio de clases')

    @api.multi
    def to_done(self, context=None):
        super(Contract, self).to_done(context=context)
        self.enroll()

    # @api.one
    # @api.depends('beneficiary_ids_2')
    @api.multi
    def enroll(self):
        self.ensure_one()

        op_roll_number_obj = self.env['op.roll.number']
        domain = [
            # ('course_id', '=', prog.course_id.id),
            # ('division_id', '=', prog.division_id.id),
            # ('student_id', '=', prog.beneficiary_id.student_id.id),
            # ('standard_id', '=', prog.standard_id.id),
            # ('batch_id', '=', prog.batch_id.id),
            # ('beneficiary_id', '=', prog.beneficiary_id.id),
            ('contract_id', '=', self.id),
            # ('operating_unit_id', '=', prog.campus_id.id),
        ]
        roll_number = op_roll_number_obj.search(domain)
        for rn in roll_number:
            rn.unlink()

        program_ids = []

        for ben in self.beneficiary_ids_2:
            program_ids += list(ben.program_ids)
        for prog in program_ids:
            # if not roll_number:
            data = {
                'course_id': prog.course_id.id,
                'division_id': prog.division_id.id,
                'student_id': prog.beneficiary_id.student_id.id,
                'standard_id': prog.standard_id.id,
                'batch_id': prog.batch_id.id,
                'roll_number': '1',
                'beneficiary_id': prog.beneficiary_id.id,
                'contract_id': self.id,
                'state': 'inactive',
                'operating_unit_id': prog.campus_id.id,
            }
            if self.date_booking_schedule:
                data.update({'schedule_reservation_date': self.date_booking_schedule})
            else:
                data.update({'schedule_reservation_date': datetime.today()})
            if self.start_date:
                data.update({'start_date': self.start_date})

            try:
                op_roll_number_obj.create(data)
            except Exception as e:
                raise except_orm('Error', u'Contacte con el administrador para solucionar el siguiente error: (%s)' % e)

    @api.multi
    def copy_active_plan(self):
        self.ensure_one()

        active_plan_id = self.plan_id.copy({
            'payment_term_ids': None,
            'amount_pay': self.plan_id.residual,
            'plan_active': True,
            'start_date': self.plan_id.start_date or datetime.today(),
            'contract_id': None,
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
                verification_id = self.env['education_contract.verification'].create({})
                self.write({'verification_id': verification_id.id})
                plan_data = self.copy_active_plan()
            except Exception as e:
                raise e

            # verification_id = self.env['education_contract.verification'].create(plan_data)
            plan_data.update({'beneficiary_ids': [(6, 0, self.beneficiary_ids_2.ids)]})
            verification_id.write(plan_data)

            self.write({
                'state': 'asigned',
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


class Plan(models.Model):
    _name = 'education_contract.plan'
    _inherit = 'education_contract.plan'

    @api.one
    @api.onchange('type', 'amount_pay', 'qty_dues', 'registration_fee', 'payment_term_ids')
    @api.depends('type', 'amount_pay', 'qty_dues', 'registration_fee', 'payment_term_ids')
    def _compute_dues(self):
        if self.type:
            if self.type == 'funded':
                payed = self._compute_voucher_sum()
                if payed >= self.registration_fee:
                    registration_residual = 0.0
                else:
                    registration_residual = self.registration_fee - payed

                if not self.contract_id:
                    if self.qty_dues:
                        amount_monthly = round((self.amount_pay - payed) / self.qty_dues, 4)
                    else:
                        amount_monthly = round((self.amount_pay - payed), 4)
                else:
                    if self.qty_dues:
                        amount_monthly = round((self.amount_pay - self.registration_fee) / self.qty_dues, 4)
                    else:
                        amount_monthly = round((self.amount_pay - self.registration_fee), 4)

                self.registration_payed = self.registration_residual == 0
                self.registration_residual = registration_residual
                self.amount_monthly = amount_monthly
                self.residual = round(self.qty_dues * self.amount_monthly, 4)

            if self.type in 'cash':
                self.residual = self.amount_pay - self._compute_voucher_sum()
