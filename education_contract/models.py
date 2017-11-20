# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser
from openerp.exceptions import ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning


#### Beneficiary
class beneficiary(models.Model):
    _name = 'education_contract.beneficiary'
    _inherits = {'op.student': 'student_id'}  #  , 'res.partner': 'partner_id'
    
    program_ids = fields.One2many('education_contract.program', 'beneficiary_id', string='Programas')
    student_id = fields.Many2one('op.student', required=True,
            string='Estudiante relacionado', ondelete='restrict',
            help='Estudiate relacionado del beneficiario', auto_join=True),
            
            
    def name_get(self,cr,uid,ids,context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr,uid,ids,context)
        
        for object in record_name:
            res.append((object.id, '%s %s %s' % (object.name or '', object.middle_name or '', object.last_name or '')))
            
        return res
    

#### Student
class student(models.Model):
    _name = 'op.student'
    _inherit = 'op.student'
    
    def name_get(self,cr,uid,ids,context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr, uid, ids, context)
        
        for object in record_name:
            res.append((object.id, '%s %s' % (object.name, object.last_name)))
            
        return res
    
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
    study_company_id = fields.Many2one('res.company', string='Sucursal')
    beneficiary_id = fields.Many2one('education_contract.beneficiary', string='Estudiante')
    contract_id = fields.Many2one('education_contract.contract', string='Contrato de estudios')
    
    
    @api.model
    def create(self, vals):
        contract_id = self._context.get('contract_id', False)
        
        if contract_id:
            vals.update({'contract_id': contract_id})
        
        res = super(program, self).create(vals)
        return res
        
        
#### Contract
class education_contract(models.Model):
    _name = 'education_contract.contract'
    _inherit = ['mail.thread']
    
    date = fields.Date(string='Fecha contrato', help="Fecha del contrato. Por defecto es la fecha del pedido de venta.")
    user_id = fields.Many2one('res.users', string='Vendedor', help='Por defecto es el creador del pedido de venta que da origen al contrato.')
    study_company_id = fields.Many2one('res.company', string='Empresa o sucursal principal')
    company_id = fields.Many2one('res.company', string='Compania', help='Interno para multiempresa')
    owner = fields.Many2one('res.partner', string='Titular')
    barcode = fields.Char('Codigo')
    sale_order_id = fields.Many2one('sale.order', string='Pedido de venta')
    beneficiary_ids = fields.Many2many('education_contract.beneficiary', relation='contract_beneficiary_rel', string='Beneficiarios Tmp')
    state = fields.Selection([('draft', 'Nuevo'), ('prechecked', 'Preverificado'), ('done', 'Aprobado'), ('asigned', 'Asignado'), ('waiting', 'Pendiente'), ('canceled', 'Anulado')], string='Estado', default='draft')
    program_ids = fields.One2many('education_contract.program', 'contract_id', string='Resumen de Programas')  #compute='_update_programs', 
    plan_id = fields.One2many('education_contract.plan', 'contract_id', string='Plan')
    payment_term_ids = fields.One2many(related='plan_id.payment_term_ids', string='Formas de pago')
    notes = fields.Text('Notas internas')
    observations = fields.Text('Observaciones')
    priority = fields.Selection([
                                    ('0','Low'),
                                    ('1','Normal'),
                                    ('2','High')],
                                    'Priority',default='1')
    kanban_state = fields.Selection(related="state")
    seller_id = fields.Many2one(related='sale_order_id.user_id')
    state_to_show = fields.Char(compute='get_kanban_state', store=True)
    marketing_manager_id = fields.Many2one('res.users', string='Gerente de Marketing')  # related to company manager
    #voucher_ids = fields.One2many(related='plan_id.payment_info_ids', string='Pagos realizados')
    
    
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
            
    
    """@api.onchange('plan_id')
    @api.depends('plan_id')
    def _compute_payment_term(self):
        payment_info_ids = self.plan_id.payment_info_ids
        import pdb; pdb.set_trace()
        payment_term_ids = []
        
        for pi in payment_info_ids:
            payment_term_ids += pi.payment_term_ids.ids
        
        payment_term_obj = self.env['education_contract.payment_term'].browse(payment_term_ids)
        payment_term_obj.write({'contract_id': self.id})
        
        self.payment_term_ids = [(6, False, payment_term_ids)]"""
    
    
    def name_get(self,cr,uid,ids,context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr,uid,ids,context)
        
        for object in record_name:
            res.append((object.id, '%s-%s %s' % (object.barcode, object.owner.firstname, object.owner.lastname)))
            
        return res
        
    
    @api.model
    def create(self, vals):
        
        if 'sale_order_id' in vals:
            sale_order_id = self.env['sale.order'].browse(vals['sale_order_id'])
                
            first_student_id = self.env['education_contract.beneficiary'].search([('name', '=', sale_order_id.partner_id.firstname), ('last_name', '=', sale_order_id.partner_id.lastname)])
                
            if not first_student_id:
                first_student_id = self.env['education_contract.beneficiary'].create({'name': sale_order_id.partner_id.firstname, 'last_name': sale_order_id.partner_id.lastname})
                
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
        
        
    """@api.multi
    def write(self, vals):
        vouchers = []
        
        plan_id = self.plan_id
        voucher_ids = plan_id.voucher_ids
        
        for v in voucher_ids:
            v.write({'education_contract_id': self.id})
            v.proforma_voucher()
            vouchers.append(v.id)
            
        vals.update({'voucher_ids': [(6, False, vouchers)]})
        
        res = super(education_contract, self).write(vals)
        
        return res"""
        

#### Plan
class plan(models.Model):
    _name = 'education_contract.plan'
    
    def name_get(self,cr,uid,ids,context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr, uid, ids, context)
        
        for object in record_name:
            res.append((object.id, '%s - %s - %s' % (object.contract_id.barcode, object.type, object.amount_pay)))
            
        return res
        
        
    @api.onchange('type')
    def clean_fields(self):
        self.amount_pay = 0.0
        self.qty_dues = 0
        self.registration_fee = 0.0
        self.registration_residual = 0.0
        self.residual = 0.0
        self.teaching_materials = ''
        
        
    """@api.one
    @api.onchange('type', 'payment_info_ids', 'qty_dues', 'amount_monthly', 'amount_pay', 'registration_fee')"""
    def _compute_residual(self):
        
        if self.type:
            if self.type in 'cash':
                self.residual = self.amount_pay - self._compute_voucher_sum()
            elif self.type in 'funded':
                self.residual = self.qty_dues * self.amount_monthly
                
                self.registration_residual = self.registration_fee - self._compute_voucher_sum()
                
                
    def _compute_voucher_sum(self):
        voucher_sum = 0.0
        for v in self.payment_info_ids:
            voucher_sum += v.amount
        
        return voucher_sum
        
        
    @api.one
    @api.depends('payment_info_ids')
    def _compute_payment_term(self):
        
        payment_term_ids = []
        payment_info_ids = self.payment_info_ids
        
        for pis in payment_info_ids:
            payment_term_ids += pis.payment_term_ids.ids
            
        payment_term_obj = self.env['education_contract.payment_term'].browse(payment_term_ids)
        
        if payment_term_obj:
            payment_term_obj.write({'plan_id': self.id})
            self.payment_term_ids = payment_term_obj
    
    
    type = fields.Selection([('funded', 'Financiado'), ('cash', 'Contado'), ('scholarship', 'Beca')], default='cash', string='Tipo de Plan', required=True)
    amount_pay = fields.Float(string='Total a pagar', digits=(6,4), required=True, default=0.00001)
    registration_fee = fields.Float(string='Valor matricula', digits=(6,4))
    qty_dues = fields.Integer(string='Cantidad de cuotas')
    amount_monthly = fields.Float(digits=(6, 4), string='Valor mensual')
    residual = fields.Float(compute='_compute_residual', digits=(6, 4), string='Saldo total a pagar')
    registration_residual = fields.Float(compute='_compute_residual', string='Saldo matricula', digits=(6, 4))
    contract_id = fields.Many2one('education_contract.contract', string='Contrato')
    #voucher_ids = fields.One2many('account.voucher', 'plan_id', string='Abonos')
    #payment_info_ids = fields.One2many('education_contract.payment_info', 'plan_id', string='Abonos')
    #payment_term_ids = fields.One2many('education_contract.payment_term', 'plan_id', string='Formas de pago')  #compute='_compute_payment_term', 
    payment_term_ids = fields.One2many('education_contract.payment_term', compute='_compute_payment_term', string='Formas de pago')  #compute='_compute_payment_term',
    payment_info_ids = fields.One2many('education_contract.payment_info', 'plan_id', string='Abonos')
    
    
#### Payment info
class payment_info(models.Model):
    _name = 'education_contract.payment_info'
    
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
 
 
#### Payment term
class payment_term(models.Model):
    _name = 'education_contract.payment_term'
    
    
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
        import pdb; pdb.set_trace()
        print('vale, bien')
        res = super(payment_term, self).create(vals)
        
        if res:
            if vals.get('transfer_id', False):
                res.transfer_id.write({'payment_term_id': res.id})
            elif vals.get('voucher_id', False):
                res.voucher_id.write({'payment_term_id': res.id})
            elif vals.get('check_id', False):
                res.check_id.write({'payment_term_id': res.id})
        
        return res
        
        
    """@api.multi
    def write(self, vals):
        import pdb; pdb.set_trace()
        print('vale, bien')
        res = super(payment_term, self).write(vals)
        
        
        return res"""
        
    
    type = fields.Selection([('credit_card', 'Tarjeta de credito'), ('cash', 'Efectivo'), ('check', 'Cheque'), ('other', 'Otro')], default='cash', string='Forma de pago', required=True)
    description_other = fields.Char('Especificacion')
    cash_sub_type = fields.Selection([('debit_card', 'Tarjeta de debito'), ('transfer', 'Transferencia'), ('cash', 'Efectivo')])
    sub_type = fields.Selection([('debit_card', 'Tarjeta de debito'), ('transfer', 'Transferencia'), ('cash', 'Efectivo')])
    voucher_id = fields.Many2one('education_contract.voucher', string='Voucher')
    check_id = fields.Many2one('education_contract.check', string='Cheque')
    transfer_id = fields.Many2one('education_contract.transfer', string='Transferencia')
    contract_id = fields.Many2one('education_contract.contract', string='Contrato')
    #account_voucher_id = fields.Many2one('account.voucher', string='Deposito abono')
    payment_info_id = fields.Many2one('education_contract.payment_info', string='Informacion de abono')
    amount = fields.Float(digits=(6, 4), string='Monto')
    plan_id = fields.Many2one('education_contract.plan', string='Plan de pagos')
    plan_id_ref = fields.Many2one(related='plan_id', string='Plan de pagos')


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
    
    
    def name_get(self,cr,uid,ids,context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr,uid,ids,context)
        
        for object in record_name:
            res.append((object.id, '%s-%s %s' % (object.voucher_number, object.auth_number, object.bank.name)))
            
        return res
        
        
#### Check
class check(models.Model):
    _name = 'education_contract.check'
    
    bank = fields.Many2one('res.bank', string='Banco')
    check_number = fields.Char('Numero de cheque')
    beneficiary = fields.Char('Beneficiario')
    payment_term_id = fields.Many2one('education_contract.payment_term', string='Forma de pago')
    amount = fields.Float(related='payment_term_id.amount', string='Monto')
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr, uid, ids, context)
        
        for object in record_name:
            res.append((object.id, '%s-%s' % (object.check_number, object.bank.name)))
            
        return res
        

#### Transfer
class transfer(models.Model):
    _name = 'education_contract.transfer'
    
    bank = fields.Many2one('res.bank', string='Banco')
    owner = fields.Char('Titular')
    auth_number = fields.Char('Numero de autorizacion')
    payment_term_id = fields.Many2one('education_contract.payment_term', string='Forma de pago')
    amount = fields.Float(related='payment_term_id.amount', string='Monto')
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr, uid, ids, context)
        
        for object in record_name:
            res.append((object.id, '%s-%s' % (object.owner, object.bank.name)))
            
        return res