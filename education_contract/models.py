# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
from dateutil import parser
from openerp.exceptions import ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning
import json


#### Beneficiary
class beneficiary(models.Model):
    _name = 'education_contract.beneficiary'
    _inherits = {
        'op.student': 'student_id',
    }  # , 'res.partner': 'partner_id'

    program_ids = fields.One2many('education_contract.program', 'beneficiary_id', string=u'Programas')
    student_id = fields.Many2one('op.student', required=True,
                                 string=u'Estudiante relacionado', ondelete='restrict',
                                 help=u'Estudiate relacionado del beneficiario', auto_join=True)
    partner_id = fields.Many2one('res.partner', _(u'Related Partner'))
    create_new = fields.Boolean(_(u'Create new beneficiary'))

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []

        record_name = self.browse(cr, uid, ids, context)

        for object in record_name:
            res.append((object.id, '%s %s %s' % (object.name or '', object.middle_name or '', object.last_name or '')))

        return res

    @api.model
    def create(self, vals):
        """
        If create_new is True and partner_id is selected, it creates a student from that partner and then attach that student to beneficiary.
        :param vals:
        :return:
        """
        id_partner = False
        partner = False

        if 'partner_id' in vals and vals.get('partner_id'):
            id_partner = vals.get('partner_id')
            partner = self.env['res.partner'].browse([id_partner])
            vals.update({'name': partner.name})
        elif 'name' in vals:
            vals.update({
                'name': vals.get('name'),
                'firstname': '%s %s' % (vals.get('name'), vals.get('middle_name', '')),
                'lastname': vals.get('last_name', ''),
                'sex': str(vals.get('gender', '')).upper(),
            })
        else:
            raise ValidationError("Debe seleccionar un cliente existente o proveer el nombre para crear uno nuevo.")

        vals.update({'customer': True})

        res = super(beneficiary, self).create(vals)

        if id_partner and partner:
            new_id_partner = res.student_id.partner_id

            if new_id_partner.id != id_partner:
                res.student_id.partner_id = partner
                new_id_partner.unlink()

        return res


#### Student
class student(models.Model):
    _name = 'op.student'
    _inherit = 'op.student'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []

        record_name = self.browse(cr, uid, ids, context)

        for object in record_name:
            res.append((object.id, '%s %s' % (object.name, object.last_name)))

        return res

    name = fields.Char('Nombre', size=128, required=False)
    middle_name = fields.Char('Segundo nombre', size=128, required=False)
    last_name = fields.Char('Apellido', size=128, required=False)
    birth_date = fields.Date('Birth Date', required=False)
    gender = fields.Selection(
        [('m', 'Hombre'), ('f', 'Mujer'),
         ('o', 'Otro')], 'Gender', required=False)
    category = fields.Many2one(
        'op.category', 'Categoria', required=False)
    course_id = fields.Many2one('op.course', 'Curso', required=False)
    batch_id = fields.Many2one('op.batch', 'Batch', required=False)
    standard_id = fields.Many2one(
        'op.standard', 'Standard', required=False)
    partner_id = fields.Many2one(
        'res.partner', 'Partner', required=False, ondelete="cascade")

    @api.model
    def create(self, vals):
        if 'name' in vals:
            context = self.env.context.copy()
            context.update({'name': vals.get('name')})
            self.env.context = context
            # self.with_context(name=vals.get('name'))
        return super(student, self).create(vals)


#### Program
class program(models.Model):
    _name = 'education_contract.program'

    @api.model
    def _get_courses_selection(self):
        courses_id = self.env['op.course'].search([])
        selection = [(x.code, x.name) for x in courses_id]
        return selection

    name = fields.Selection(selection='_get_courses_selection', string='Nombre del Programa')
    qty_years = fields.Integer('Anios')
    study_company_id = fields.Many2one('res.company', string='Sucursal')  ## Deprecated or related campus_id.company_id
    campus_id = fields.Many2one('operating.unit', string='Sucursal')
    beneficiary_id = fields.Many2one('education_contract.beneficiary', string='Estudiante')
    contract_id = fields.Many2one('education_contract.contract', string='Contrato de estudios')

    @api.model
    def create(self, vals):
        contract_id = self._context.get('contract_id', False)

        if contract_id:
            vals.update({'contract_id': contract_id})

        res = super(program, self).create(vals)
        return res


PLAN_TYPES = {'funded': 'Financiado', 'cash': 'Contado', 'scholarship': 'Beca'}


#### Contract
class education_contract(models.Model):
    _name = 'education_contract.contract'
    _inherit = ['mail.thread']

    def get_beneficiary_names(self):
        names = []

        for id in self.beneficiary_ids:
            names.append('%s %s' % (id.name, id.last_name))

        return names

    def get_plan_id_type(self):
        return PLAN_TYPES.get(self.plan_id.type, '')

    def get_done_amount(self):
        payment_term_ids = self.env['education_contract.payment_term'].search(
            [('id', 'in', self.payment_term_ids.ids), ('state', 'in', ['done', 'to_advance', 'processed'])])

        sum = 0.0

        for pt in payment_term_ids:
            sum += pt.amount

        return sum

    def get_not_done_amount(self):
        if self.plan_id.type in 'cash':
            return self.plan_id.amount_pay - self.get_done_amount()
        elif self.plan_id.type in 'funded':
            return self.plan_id.registration_fee - self.get_done_amount()
        else:
            return 0.0

    def get_monthly_data(self):
        if self.plan_id.type in ['funded']:
            return '%d - %.2f' % (self.plan_id.qty_dues, self.plan_id.amount_monthly)

    def get_payment_amount_by_type(self, type=None, sub_type=None):
        domain = []

        if type:
            if type not in ['card']:
                domain = [('type', 'in', [type]), ('id', 'in', self.payment_term_ids.ids),
                          ('state', 'in', ['done', 'to_advance'])]
            else:
                domain = ['|', ('type', 'in', ['credit_card']), ('cash_sub_type', 'in', ['debit_card']),
                          ('id', 'in', self.payment_term_ids.ids), ('state', 'in', ['done', 'to_advance'])]

        elif sub_type:
            domain = [('cash_sub_type', 'in', ['cash', 'transfer']), ('id', 'in', self.payment_term_ids.ids),
                      ('state', 'in', ['done', 'to_advance', 'processed'])]

        payment_term_ids = self.env['education_contract.payment_term'].search(domain)

        sum = 0.0

        for pt in payment_term_ids:
            sum += pt.amount

        return sum

    def get_payment_term_info(self):
        payment_term_ids = self.env['education_contract.payment_term'].search(
            ['|', ('type', 'in', ['credit_card']), ('cash_sub_type', 'in', ['debit_card']),
             ('id', 'in', self.payment_term_ids.ids), ('state', 'in', ['done', 'to_advance'])])

        data = []

        for pt in payment_term_ids:
            data.append('%s - %s - %s' % (pt.voucher_id.card_name, pt.voucher_id.auth_number, pt.voucher_id.bank.name))

        return data

    def get_payment_term_check_info(self):
        payment_term_ids = self.env['education_contract.payment_term'].search(
            [('type', 'in', ['check']), ('id', 'in', self.payment_term_ids.ids),
             ('state', 'in', ['done', 'to_advance'])])

        data = []

        for pt in payment_term_ids:
            data.append('%s - %s' % (pt.check_id.check_number, pt.check_id.bank.name))

        return data

    def get_program_count_by_name(self):
        sum_ilvem = 0
        sum_charlotte = 0
        sum_tomatis = 0

        for prog in self.program_ids:
            if prog.name in ['01']:
                sum_charlotte += 1
            elif prog.name in ['02']:
                sum_ilvem += 1
            elif prog.name in ['03']:
                sum_tomatis += 1

        progs = []

        if sum_charlotte:
            progs.append({'name': 'CHARLOTTE', 'value': sum_charlotte})
        if sum_ilvem:
            progs.append({'name': 'ILVEM', 'value': sum_ilvem})
        if sum_tomatis:
            progs.append({'name': 'TOMATIS', 'value': sum_tomatis})

        return progs

    def get_phone_numbers(self):
        phones = []

        for bi in self.beneficiary_ids:
            student = bi.student_id
            partner_id = student.partner_id

            phones.append(partner_id.mobile)
            phones.append(partner_id.phone)

        return phones

    def get_total_cash(self):
        payment_term_ids = self.env['education_contract.payment_term'].search(
            [('cash_sub_type', 'in', ['cash']), ('id', 'in', self.payment_term_ids.ids), ('state', 'in', ['done'])])

        sum = 0.0

        for pt in payment_term_ids:
            sum += pt.amount

        return sum

    def get_total_check(self):
        payment_term_ids = self.env['education_contract.payment_term'].search(
            [('type', 'in', ['check']), ('id', 'in', self.payment_term_ids.ids), ('state', 'in', ['done'])])

        sum = 0.0

        for pt in payment_term_ids:
            sum += pt.amount

        return sum

    def get_total_transfer(self):
        payment_term_ids = self.env['education_contract.payment_term'].search(
            [('cash_sub_type', 'in', ['transfer']), ('id', 'in', self.payment_term_ids.ids), ('state', 'in', ['done'])])

        sum = 0.0

        for pt in payment_term_ids:
            sum += pt.amount

        return sum

    def get_total_voucher(self):
        payment_term_ids = self.env['education_contract.payment_term'].search(
            ['|', ('cash_sub_type', 'in', ['debit_card']), ('type', 'in', ['credit_card']),
             ('id', 'in', self.payment_term_ids.ids), ('state', 'in', ['done'])])

        sum = 0.0

        for pt in payment_term_ids:
            sum += pt.amount

        return sum

    def get_total_advance(self):
        payment_term_ids = self.env['education_contract.payment_term'].search(
            [('type', 'in', ['cash']), ('id', 'in', self.payment_term_ids.ids), ('state', 'in', ['to_advance'])])

        sum = 0.0

        for pt in payment_term_ids:
            sum += pt.amount

        return sum

    def get_cash_advances_summary(self):
        payment_term_ids = self.env['education_contract.payment_term'].search(
            [('type', 'in', ['cash']), ('id', 'in', self.payment_term_ids.ids), ('state', 'in', ['to_advance'])])

        advances = []

        for pt in payment_term_ids:
            salary_advance_id = pt.salary_advance_id
            advances.append({
                'date': salary_advance_id.date,
                'user_id': salary_advance_id.seller_id.name,
                'concept': salary_advance_id.salary_advance_id.reason,
                'amount': pt.amount
            })

        return advances

    date = fields.Date(string='Fecha contrato', help="Fecha del contrato. Por defecto es la fecha del pedido de venta.")
    user_id = fields.Many2one('res.users', string='Vendedor',
                              help='Por defecto es el creador del pedido de venta que da origen al contrato.')
    study_company_id = fields.Many2one('res.company',
                                       string='Empresa o sucursal principal')  ## Deprecated or related campus_id.company_id
    campus_id = fields.Many2one('operating.unit', string='Sucursal')
    company_id = fields.Many2one('res.company', string='Compania', help='Interno para multiempresa')
    owner = fields.Many2one('res.partner', string='Titular')
    barcode = fields.Char('Codigo')
    sale_order_id = fields.Many2one('sale.order', string='Pedido de venta')
    beneficiary_ids = fields.Many2many('education_contract.beneficiary', relation='contract_beneficiary_rel',
                                       string='Beneficiarios Tmp')
    state = fields.Selection(
        [('draft', 'Nuevo'), ('prechecked', 'Preverificado'), ('done', 'Aprobado'), ('validated', 'Conciliado'),
         ('asigned', 'Asignado'), ('waiting', 'Pendiente'), ('canceled', 'Anulado')], string='Estado', default='draft')
    program_ids = fields.One2many('education_contract.program', 'contract_id',
                                  string='Resumen de Programas')  # compute='_update_programs',
    plan_id = fields.One2many('education_contract.plan', 'contract_id', string='Plan')
    payment_term_ids = fields.One2many(related='plan_id.payment_term_ids', reverse='contract_id',
                                       string='Formas de pago')
    notes = fields.Text('Notas internas')
    observations = fields.Text('Observaciones')
    priority = fields.Selection([
        ('0', 'Low'),
        ('1', 'Normal'),
        ('2', 'High')],
        'Priority', default='1')
    kanban_state = fields.Selection(related="state")
    seller_id = fields.Many2one(related='sale_order_id.user_id')
    state_to_show = fields.Char(compute='get_kanban_state', store=True)
    marketing_manager_id = fields.Many2one('res.users', string='Gerente de Marketing')
    contract_conciliation_id = fields.One2many('education_contract.conciliation', 'contract_id',
                                               string='Conciliacion de contrato')

    def get_kanban_state(self):
        for record in self:
            if record.state in 'draft':
                return 'Nuevo'
            else:
                return 'Otro estado'

    @api.constrains('plan_id')
    def _check_plan(self):
        for record in self:
            plan = record.plan_id

            if len(plan) > 1:
                raise ValidationError("Solo se permite un Plan de pago por Contrato.")

            type = plan.type

            if type in 'funded':
                if not plan.qty_dues or not plan.registration_fee or not plan.amount_pay:
                    raise ValidationError("Debe registrar datos para los campos obligatorios del plan de pago.")

            if type in 'cash':
                if not plan.amount_pay:
                    raise ValidationError("Debe registrar datos para los campos obligatorios del plan de pago.")

    def validate_filled(self):
        if not self.beneficiary_ids:
            return False

        if not self.program_ids:
            return False

        if not self.plan_id:
            return False

        if not self.payment_term_ids:
            return False

        return True

    @api.multi
    def to_draft(self, context=None):
        print('Cambiar a Borrador')
        self.write({'state': 'draft'})

    @api.multi
    def to_prechecked(self, context=None):
        print('Cambiar a Preverificado')

        filled = self.validate_filled()

        if not filled:
            raise ValidationError("Debe completar todos los datos del contrato para cambiar a estado 'Pre-verificado'.")
        else:
            self.write({'state': 'prechecked'})

    @api.multi
    def to_done(self, context=None):
        print('Cambiar a Aprobado')

        filled = self.validate_filled()

        if not filled:
            raise ValidationError("Debe completar todos los datos del contrato para cambiar a estado 'Aprobado'.")
        else:
            self.write({'state': 'done'})

    def to_waiting(self, cr, uid, ids, context=None):
        print('Cambiar a Pendiente')
        self.pool.get('education_contract.contract').browse(cr, uid, ids).write({'state': 'waiting'})

    def to_validated(self, cr, uid, ids, context=None):
        print('Cambiar a Conciliado')
        records = self.pool.get('education_contract.contract').browse(cr, uid, ids)
        payment_terms = records.payment_term_ids

        valid = True

        for pt in payment_terms:
            if pt.state not in ['done', 'processed']:
                valid = False
                break

        if not valid:
            raise ValidationError("""Debe conciliar todas las formas de pago del contrato para cambiar a estado 'Conciliado'.
                                    Si existe algun anticipo pendiente, este debe ser generado antes de continuar.""")
        else:
            self.pool.get('education_contract.contract').browse(cr, uid, ids).write({'state': 'validated'})

    def to_canceled(self, cr, uid, ids, context=None):
        print('Cambiar a Cancelado')
        self.pool.get('education_contract.contract').browse(cr, uid, ids).write({'state': 'canceled'})

    @api.multi
    def to_asigned(self, context=None):
        print('Cambiar a Asignado')

        filled = self.validate_filled()

        if not filled:
            raise ValidationError("Debe completar todos los datos del contrato para cambiar a estado 'Asignado'.")
        else:
            self.write({'state': 'asigned'})

    def _update_programs(self):
        p_ids = []

        for record in self:
            bs = [b for b in record.beneficiary_ids]

            for s in bs:
                ps = [p.id for p in s.program_ids]
                p_ids += ps

            record.program_ids = [(6, False, p_ids)]

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []

        record_name = self.browse(cr, uid, ids, context)

        for object in record_name:
            res.append((object.id, '%s-%s %s' % (object.barcode, object.owner.firstname, object.owner.lastname)))

        return res

    @api.model
    def create(self, vals):
        if 'sale_order_id' in vals:
            sale_order_id = self.env['sale.order'].browse(vals['sale_order_id'])

            first_student_id = self.env['education_contract.beneficiary'].search(
                [('firstname', '=', sale_order_id.partner_id.firstname),
                 ('last_name', '=', sale_order_id.partner_id.lastname)])

            if not first_student_id:
                first_student_id = self.env['education_contract.beneficiary'].create({
                    'firstname': sale_order_id.partner_id.firstname,
                    'name': sale_order_id.partner_id.firstname,
                    'last_name': sale_order_id.partner_id.lastname})

            user_id = sale_order_id.user_id.id

            sale_team_ids = self.env['crm.case.section'].search([])
            sale_team = None

            for team in sale_team_ids:
                company_ids = team.company_ids

                for company in company_ids:
                    if company.id == sale_order_id.company_id.id:
                        sale_team = team
                        continue

            sale_team_leader_id = sale_team.user_id.id or None

            if first_student_id:
                vals = {
                    'date': sale_order_id.date_order,
                    'user_id': user_id,
                    'company_id': sale_order_id.company_id.id,
                    'owner': sale_order_id.partner_id.id,
                    'sale_order_id': sale_order_id.id,
                    'beneficiary_ids': [(6, 0, [first_student_id.id])],
                    'marketing_manager_id': sale_team_leader_id
                }

                plan_id = self.env['education_contract.plan'].create({
                    'type': 'cash',
                    'amount_pay': sale_order_id.amount_total,
                    'qty_dues': 0,
                    'residual': sale_order_id.amount_total,
                })

                if plan_id:
                    vals.update({'plan_id': [(6, False, [plan_id.id])]})

                res = super(education_contract, self).create(vals)

                return res

        return False

    @api.onchange('user_id')
    def onchange_seller_id(self):

        if self.user_id:
            sale_team_ids = self.env['crm.case.section'].search([])

            sale_team = None

            for team in sale_team_ids:
                company_ids = team.company_ids

                for company in company_ids:
                    if company.id == self.sale_order_id.company_id.id:
                        if self.user_id.id in team.member_ids.ids:
                            sale_team = team
                            continue

            if sale_team:
                sale_team_leader_id = sale_team.user_id or None
                self.marketing_manager_id = sale_team_leader_id or None
            else:
                self.marketing_manager_id = None

        else:
            self.marketing_manager_id = None


#### Plan
TYPE = {'funded': 'Financiado', 'cash': 'Contado', 'scholarship': 'Beca'}


class plan(models.Model):
    _name = 'education_contract.plan'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []

        record_name = self.browse(cr, uid, ids, context)

        for object in record_name:
            res.append((object.id,
                        '%s - %s - %s' % (object.contract_id.barcode, TYPE.get(object.type, ''), object.amount_pay)))

        return res

    @api.onchange('type')
    def clean_fields(self):
        if self.type:
            if self.type == 'cash':
                self.qty_dues = 0.0
                self.registration_fee = 0.0
                self.registration_residual = 0.0
                self.amount_monthly = 0.0

        """self.qty_dues = 0
        self.registration_fee = 0.0
        self.registration_residual = 0.0
        self.residual = 0.0
        self.teaching_materials = ''
        self.amount_monthly = 0.0"""

    @api.one
    @api.depends('type', 'amount_pay', 'amount_monthly')
    def _compute_dues(self):
        if self.type:
            if self.type == 'funded':
                residual = self.amount_pay - self.registration_fee
                if self.amount_monthly == 0:
                    self.amount_monthly = self.amount_pay

                div = residual / self.amount_monthly
                cos = residual % self.amount_monthly

                if cos == 0:
                    self.qty_dues = div
                else:
                    self.qty_dues = div + 1

    @api.one
    @api.depends('type', 'amount_pay', 'payment_term_ids')
    def _compute_residual(self):
        if self.type:
            if self.type in 'cash':
                self.residual = self.amount_pay - self._compute_voucher_sum()
            elif self.type in 'funded':
                self.residual = self.qty_dues * self.amount_monthly

                self.registration_residual = self.registration_fee - self._compute_voucher_sum()

    def _compute_voucher_sum(self):
        voucher_sum = 0.0
        # for v in self.payment_info_ids:
        for v in self.payment_term_ids:
            voucher_sum += v.amount

        return voucher_sum

    """@api.one
    @api.depends('payment_info_ids')
    def _compute_payment_term(self):

        payment_term_ids = []
        payment_info_ids = self.payment_info_ids

        for pis in payment_info_ids:
            payment_term_ids += pis.payment_term_ids.ids

        payment_term_obj = self.env['education_contract.payment_term'].browse(payment_term_ids)

        if payment_term_obj:
            payment_term_obj.write({'plan_id': self.id})
            self.payment_term_ids = payment_term_obj"""

    type = fields.Selection([('funded', 'Financiado'), ('cash', 'Contado'), ('scholarship', 'Beca')], default='cash',
                            string='Tipo de Plan', required=True)
    amount_pay = fields.Float(string='Total a pagar', digits=(6, 4), required=True, default=0.00001)
    registration_fee = fields.Float(string='Valor matricula', digits=(6, 4))
    qty_dues = fields.Integer(string='Cantidad de cuotas', compute='_compute_dues')
    amount_monthly = fields.Float(digits=(6, 4), string='Valor mensual')
    residual = fields.Float(compute='_compute_residual', digits=(6, 4), string='Saldo total a pagar')
    registration_residual = fields.Float(compute='_compute_residual', string='Saldo matricula', digits=(6, 4))
    contract_id = fields.Many2one('education_contract.contract', string='Contrato')
    payment_term_ids = fields.One2many('education_contract.payment_term', 'plan_id',
                                       string='Formas de pago')  # compute='_compute_payment_term',
    # payment_info_ids = fields.One2many('education_contract.payment_info', 'plan_id', string='Abonos')


#### Payment info
"""class payment_info(models.Model):
    _name = 'education_contract.payment_info'

    @api.one
    @api.onchange('payment_term_ids', 'amount', 'plan_id')
    def _compute_residual(self):
        sum = 0.0

        for pt in self.payment_term_ids:
            sum += pt.amount

        self.residual = self.amount - sum

    amount = fields.Float(digits=(6, 4), string='Monto')
    residual = fields.Float(compute='_compute_residual', digits=(6, 4), string='Saldo', store=True)
    payment_term_ids = fields.One2many('education_contract.payment_term', 'payment_info_id', string='Forma de pago')
    plan_id = fields.Many2one('education_contract.plan', string='Plan de pagos')
    contract_id = fields.Many2one('education_contract.contract', string='Contrato')

    @api.model
    def create(self, vals):
        if 'residual' in vals and 'amount' in vals:
            if float(vals.get('residual', '0.0')) > float('0.0'):
                raise ValidationError("El saldo de los pagos debe ser cero.")

        return super(payment_info, self).create(vals)

    @api.multi
    def write(self, vals):
        if self.residual > 0:
            raise ValidationError("El saldo de los pagos debe ser cero.")

        return super(payment_info, self).write(vals)"""


#### Payment term
class payment_term(models.Model):
    _name = 'education_contract.payment_term'

    @api.one
    @api.depends('state')
    @api.onchange('state')
    def validate_contract(self):
        # payment_term_ids = self.plan_id.contract_id.payment_term_ids
        payment_term_ids = self.plan_id.payment_term_ids

        all_done = True

        for pt in payment_term_ids:
            if pt.state not in ['done', 'processed']:
                all_done = False
                break

        if all_done:
            self.plan_id.contract_id.write({'state': 'validated'})

    @api.one
    def generate_voucher(self, state):

        voucher_data = {
            'partner_id': self.plan_id.contract_id.owner.id,
            'amount': abs(self.amount),
            'journal_id': self.payment_mode_id.journal_id.id,
            'account_id': self.payment_mode_id.journal_id.default_debit_account_id.id,
            'type': 'receipt',
            'reference': self.plan_id.contract_id.barcode,
            'company_id': self.payment_mode_id.journal_id.company_id.id,
        }

        voucher_id = self.env['account.voucher'].create(voucher_data)
        voucher_id.proforma_voucher()

        self.write({'account_voucher_id': voucher_id.id, 'state': state})

    @api.one
    def processed(self):
        self.write({'state': 'processed'})

    @api.one
    def confirm(self):
        self.generate_voucher('done')
        self.validate_contract()

    @api.one
    def cancel(self):
        if self.account_voucher_id:
            self.account_voucher_id.cancel_voucher()
            self.account_voucher_id.unlink()

        if self.salary_advance_id:
            self.salary_advance_id.unlink()

        self.write({'state': 'cancel'})
        self.plan_id.contract_id.write({'state': 'draft'})

        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    @api.one
    def advance(self):
        self.generate_voucher('to_advance')
        self.validate_contract()

    @api.onchange('sub_type')
    def clean_fields_sub_type(self):
        self.clean()

    @api.onchange('cash_sub_type')
    def clean_fields_cash_sub_type(self):
        self.clean()

    @api.onchange('type')
    def clean_fields(self):
        self.clean()
        self.cash_sub_type = ''

    def clean(self):
        self.description_other = ''
        self.sub_type = ''

        if self.voucher_id:
            self.voucher_id.unlink()

        if self.check_id:
            self.check_id.unlink()

        if self.transfer_id:
            self.transfer_id.unlink()

    @api.model
    def create(self, vals):
        res = super(payment_term, self).create(vals)

        if res:
            if vals.get('transfer_id', False):
                res.transfer_id.write({'payment_term_id': res.id})
            elif vals.get('voucher_id', False):
                res.voucher_id.write({'payment_term_id': res.id})
            elif vals.get('check_id', False):
                res.check_id.write({'payment_term_id': res.id})

        return res

    @api.one
    def _compute_payment_mode(self):
        if not self.type:
            return False

        payment_mode_id = self.env['education_contract.payment_mode'].search([('code', '=', self.type)])

        if not payment_mode_id:
            raise ValidationError("Debe configurar un modo de pago de tipo %s." % self.type)

        if not payment_mode_id.journal_id:
            raise ValidationError("Debe configurar un Diario contable para el modo de pago de tipo %s." % self.type)

        """if not payment_mode_id.asset_account_id:
            raise ValidationError("Debe configurar una cuenta de activos para el modo de pago de tipo %s." % self.type)"""

        self.payment_mode_id = payment_mode_id

    @api.multi
    def _is_visible(self):

        for record in self:
            invisible = False

            if record.contract_state not in ['prechecked']:
                invisible = True

            if record.state in ['done', 'to_advance', 'processed']:
                invisible = True

            if record.cash_sub_type not in ['cash']:
                invisible = True

            record.invisible = invisible

    type = fields.Selection(
        [('credit_card', 'Tarjeta de credito'), ('cash', 'Efectivo'), ('check', 'Cheque'), ('other', 'Otro')],
        default='cash', string='Forma de pago', required=True)
    description_other = fields.Char('Especificacion')
    cash_sub_type = fields.Selection(
        [('debit_card', 'Tarjeta de debito'), ('transfer', 'Transferencia'), ('cash', 'Efectivo')])
    sub_type = fields.Selection(
        [('debit_card', 'Tarjeta de debito'), ('transfer', 'Transferencia'), ('cash', 'Efectivo')])
    voucher_id = fields.Many2one('education_contract.voucher', string='Voucher')
    check_id = fields.Many2one('education_contract.check', string='Cheque')
    transfer_id = fields.Many2one('education_contract.transfer', string='Transferencia')
    contract_id = fields.Many2one('education_contract.contract', string='Contrato')
    account_voucher_id = fields.Many2one('account.voucher', string='Deposito abono')
    # payment_info_id = fields.Many2one('education_contract.payment_info', string='Informacion de abono')
    amount = fields.Float(digits=(6, 4), string='Monto')
    plan_id = fields.Many2one('education_contract.plan', string='Plan de pagos')
    plan_id_ref = fields.Many2one(related='plan_id', string='Plan de pagos')
    state = fields.Selection(
        [('draft', 'Nuevo'), ('done', 'Confirmado'), ('to_advance', 'Para anticipo'), ('cancel', 'Cancelado'),
         ('processed', 'Procesado')], default='draft', string='Estado')
    payment_mode_id = fields.Many2one('education_contract.payment_mode', compute='_compute_payment_mode',
                                      string='Modo de pago')
    salary_advance_id = fields.Many2one('education_contract.advance', string='Avanse de salario')
    contract_state = fields.Selection(related='plan_id.contract_id.state', store=True)
    invisible = fields.Boolean('Invisible', compute='_is_visible', default=True)


class payment_mode(models.Model):
    _name = 'education_contract.payment_mode'

    code = fields.Char('Codigo')  # cash (Efectivo), credit_card (Banco), check (Banco)
    name = fields.Char('Nombre')
    journal_id = fields.Many2one('account.journal', string='Diario contable')
    # account_id = fields.Many2one('account.account', string='Cuenta contable')
    # asset_account_id = fields.Many2one('account.account', string='Cuenta de activos')
    # income_account_id = fields.Many2one('account.account', string='Cuenta de ingresos')


#### Voucher
class voucher(models.Model):
    _name = 'education_contract.voucher'

    date = fields.Date('Fecha')
    card_name = fields.Char('Nombre de tarjeta')  # revisar que sea un nomenclador
    voucher_number = fields.Char('Numero de voucher')
    auth_number = fields.Char('Numero de autorizacion')
    bank = fields.Many2one('res.bank', string='Banco')
    payment_term_id = fields.Many2one('education_contract.payment_term', string='Forma de pago')
    amount = fields.Float(related='payment_term_id.amount', string='Monto')

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []

        record_name = self.browse(cr, uid, ids, context)

        for object in record_name:
            res.append((object.id, '%s-%s %s' % (object.voucher_number, object.auth_number, object.bank.name)))

        return res


#### Check
class check(models.Model):
    _name = 'education_contract.check'
    _rec_name = 'check_number'

    date = fields.Date('Fecha')
    bank = fields.Many2one('res.bank', string='Banco')
    check_number = fields.Char('Numero de cheque')
    beneficiary = fields.Char('Beneficiario')
    payment_term_id = fields.Many2one('education_contract.payment_term', string='Forma de pago')
    amount = fields.Float(related='payment_term_id.amount', string='Monto')

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []

        record_name = self.browse(cr, uid, ids, context)

        for object in record_name:
            res.append((object.id, '%s-%s' % (object.check_number, object.bank.name)))

        return res


#### Transfer
class transfer(models.Model):
    _name = 'education_contract.transfer'

    date = fields.Date('Fecha')
    bank = fields.Many2one('res.bank', string='Banco')
    owner = fields.Char('Titular')
    auth_number = fields.Char('Numero de autorizacion')
    payment_term_id = fields.Many2one('education_contract.payment_term', string='Forma de pago')
    amount = fields.Float(related='payment_term_id.amount', string='Monto')

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []

        record_name = self.browse(cr, uid, ids, context)

        for object in record_name:
            res.append((object.id, '%s-%s' % (object.owner, object.bank.name)))

        return res
