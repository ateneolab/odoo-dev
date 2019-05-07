# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api, _
from openerp.exceptions import except_orm
import datetime


class ContractVerification(models.Model):
    _name = 'education_contract.verification'
    _description = u'Verificación de contrato'

    @api.multi
    def print_verification(self):
        self.ensure_one()
        self.enroll()
        return {
            'type': 'ir.actions.report.xml',
            'report_name': 'education_contract_collection_plan.report_verification_template',
            'context': self._context,
        }

    # @api.multi
    # def unlink(self):
    #     raise except_orm('Error', _(u"You can't remove a collection plan, you can only edit it."))

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []

        record_name = self.browse(cr, uid, ids, context)

        for object in record_name:
            res.append((object.id,
                        '%s-%s' % (object.contract_id.barcode or '', object.verification_date or '')))

        return res

    @api.one
    def reschedule_plan(self):
        if self.plan_id:
            if not self.plan_id.start_date:
                self.plan_id.start_date = self.start_date
            self.plan_id.reschedule()

    @api.one
    def generate_collection_plan(self):
        plan_id = self.plan_id.copy({
            'contract_id': None
        })

        for pt in self.plan_id.payment_term_ids:
            new_pt = pt.copy({
                'plan_id': plan_id.id,
                'fixed_plan_id': plan_id.id,
            })

            plan_id.write({
                'payment_term_ids': [(4, new_pt.id)]
            })

        data = {
            'active_plan_id': plan_id.id,
            'start_date': plan_id.start_date,
            'contract_id': self.contract_id.id,
            'verification_id': self.id
        }

        collection_id = self.env['collection_plan.collection_plan'].create(data)

        self.write({
            'collection_plan_id': collection_id.id,
            'contract_id': self.contract_id.id,
            'start_date': plan_id.start_date,
            'state': 'generated'
        })

        plan_id.write({'collection_plan_id': collection_id.id})

        self.contract_id.write({'collection_id': collection_id.id})

        self.update_references()

        self.enroll()

    @api.multi
    def update_references(self):
        self.write({'verify_user_id': self._uid, 'date': datetime.datetime.today()})

    @api.multi
    def enroll(self):
        self.ensure_one()
        program_ids = []
        for ben in self.beneficiary_ids:
            # program_ids.append(ben.program_ids)
            program_ids += list(ben.program_ids)
        for prog in program_ids:
            roll_number = self.env['op.roll.number'].search(
                [
                    ('course_id', '=', prog.course_id.id),
                    ('division_id', '=', prog.division_id.id),
                    ('student_id', '=', prog.beneficiary_id.student_id.id),
                    ('standard_id', '=', prog.standard_id.id),
                    ('batch_id', '=', prog.batch_id.id),
                    ('beneficiary_id', '=', prog.beneficiary_id.id),
                    ('contract_id', '=', self.contract_id.id),
                ]
            )
            if not roll_number:
                self.env['op.roll.number'].create({
                    'course_id': prog.course_id.id,
                    'division_id': prog.division_id.id,
                    'student_id': prog.beneficiary_id.student_id.id,
                    'standard_id': prog.standard_id.id,
                    'batch_id': prog.batch_id.id,
                    'roll_number': '1',
                    'beneficiary_id': prog.beneficiary_id.id,
                    'contract_id': self.contract_id.id,
                    'state': 'active'
                })
            else:
                roll_number.write({'state': 'active'})

    def get_cash_amount(self):
        plan_id = self.contract_id.plan_id
        payment_term_ids = plan_id.payment_term_ids

        sum = 0.0

        for pt in payment_term_ids:
            if pt.type == 'cash' and pt.cash_sub_type == 'cash':
                sum += pt.amount

        return sum

    def get_check_amount(self):
        plan_id = self.contract_id.plan_id
        payment_term_ids = plan_id.payment_term_ids

        sum = 0.0

        for pt in payment_term_ids:
            if pt.type == 'check':
                sum += pt.amount

        return sum

    def get_credit_card_amount(self):
        plan_id = self.contract_id.plan_id
        payment_term_ids = plan_id.payment_term_ids

        sum = 0.0

        for pt in payment_term_ids:
            if pt.type == 'credit_card':
                sum += pt.amount

        return sum

    def get_plan_detail(self):
        plan_id = self.contract_id.plan_id

        data = """"""

        data += 'Total: %d \n' % (plan_id.amount_pay)
        data += 'Cuotas: %d \n' % (plan_id.qty_dues)
        data += 'Montos: %d' % (plan_id.amount_monthly)

        return data

    @api.one
    def to_signed(self):
        self.verify_user_id = self._uid
        self.write({'state': 'signed'})

    operating_unit_id = fields.Many2one(related='contract_id.campus_id', store=True, string='Sucursal')
    contract_id = fields.Many2one('education_contract.contract', _('Contrato'))
    roll_number_ids = fields.One2many(related='contract_id.roll_number_ids', string=u'Matrículas')
    contract_date = fields.Date(_('Fecha de contrato'), related='contract_id.date')
    verification_date = fields.Date(u'Fecha de verificación')
    agreement_duration = fields.Integer(_(u'Duración del acuerdo (Meses)'), default=24)
    verification_place = fields.Selection([('office', _('Oficina')), ('home', _('Domicilio')), ('work', _('Trabajo'))],
                                          default='home')
    user_id = fields.Many2one(related='contract_id.seller_id', string=u'Vendedor')
    verify_user_id = fields.Many2one('res.users', string=_('Verificado por'))
    collection_plan_id = fields.Many2one('collection_plan.collection_plan', _('Plan de cobranzas'))
    plan_id = fields.Many2one('education_contract.plan', _('Plan de pagos'))
    payment_term_ids = fields.One2many(related='plan_id.payment_term_ids', string=u'Pagos')
    beneficiary_ids = fields.One2many('education_contract.beneficiary', 'verification_id', string=_('Beneficiarios'))

    collections_phone = fields.Char(u'Teléfono de cobranzas')
    partner_id = fields.Many2one(related='contract_id.owner', string='Titular')
    state = fields.Selection(
        [
            ('new', _(u'Nuevo')),
            ('generated', _(u'Generado')),
            ('signed', _(u'Firmado'))
        ],
        required=True,
        default='new'
    )


class CollectionPlan(models.Model):
    _inherit = 'collection_plan.collection_plan'
    _description = 'Plan de cobranzas'

    verification_id = fields.Many2one('education_contract.verification', 'collection_plan_id')
