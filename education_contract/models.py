# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser
from openerp.exceptions import ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning


class beneficiary(models.Model):
    _name = 'education_contract.beneficiary'
    _inherits = {'op.student': 'student_id'}  #  , 'res.partner': 'partner_id'
    
    program_ids = fields.One2many('education_contract.program', 'beneficiary_id', string='Programas')
    student_id = fields.Many2one('op.student', required=True,
            string='Estudiante relacionado', ondelete='restrict',
            help='Estudiate relacionado del beneficiario', auto_join=True),
    """partner_id = fields.Many2one('res.partner', required=True,
            string='Partner relacionado', ondelete='restrict',
            help='Partner relacionado del beneficiario', auto_join=True),"""
            
            
    def name_get(self,cr,uid,ids,context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr,uid,ids,context)
        
        for object in record_name:
            res.append((object.id, '%s %s %s' % (object.name or '', object.middle_name or '', object.last_name or '')))
            
        return res
    

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
    payment_term_ids = fields.One2many('education_contract.payment_term', 'contract_id', string='Formas de pago')
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
    
    
    def get_kanban_state(self):
        import pdb; pdb.set_trace()
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
                if not plan.qty_dues or not plan.registration_fee or not plan.initial_subscription or not plan.amount_pay:
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
            
            if first_student_id:
                vals = {
                    'date': sale_order_id.date_order,
                    'user_id': sale_order_id.user_id.id,
                    'company_id': sale_order_id.company_id.id,
                    'owner': sale_order_id.partner_id.id,
                    'sale_order_id': sale_order_id.id,
                    'beneficiary_ids': [(6, 0, [first_student_id.id])],
                }
                
                res = super(education_contract, self).create(vals)
            
                return res
            
        return False
        
        
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
        self.initial_subscription = 0.0
        self.residual = 0.0
        self.teaching_materials = ''
    
    type = fields.Selection([('funded', 'Financiado'), ('cash', 'Contado'), ('scholarship', 'Beca')], default='cash', string='Tipo de Plan', required=True)
    amount_pay = fields.Float(string='Total a pagar', digits=(6,4), required=True, default=0.00001)
    qty_dues = fields.Integer(string='Cantidad de cuotas')
    registration_fee = fields.Float(string='Abono de matricula', digits=(6,4))
    initial_subscription = fields.Float(string='Abono inicial', digits=(6,4))
    contract_id = fields.Many2one('education_contract.contract', string='Contrato')  # , required=True
    residual = fields.Float('Saldo a pagar', digits=(6, 4))
    teaching_materials = fields.Char('Material didactico')
    
    
class payment_term(models.Model):
    _name = 'education_contract.payment_term'
    
    
    @api.onchange('cash_sub_type')
    def clean_fields(self):
        self.clean()
        
    @api.onchange('type')
    def clean_fields(self):
        self.clean()
        self.cash_sub_type = ''
        
    def clean(self):
        self.description_other = ''
        self.sub_type = ''
        self.voucher_id = None
        self.check_id = None
        self.transfer_id = None
        
    
    type = fields.Selection([('credit_card', 'Tarjeta de credito'), ('cash', 'Efectivo'), ('check', 'Cheque'), ('other', 'Otro')], default='cash', string='Forma de pago', required=True)
    description_other = fields.Char('Especificacion')
    cash_sub_type = fields.Selection([('debit_card', 'Tarjeta de debito'), ('transfer', 'Transferencia'), ('cash', 'Efectivo')])
    sub_type = fields.Selection([('debit_card', 'Tarjeta de debito'), ('transfer', 'Transferencia'), ('cash', 'Efectivo')])
    voucher_id = fields.Many2one('education_contract.voucher', string='Voucher')
    check_id = fields.Many2one('education_contract.check', string='Cheque')
    transfer_id = fields.Many2one('education_contract.transfer', string='Transferencia')
    contract_id = fields.Many2one('education_contract.contract', string='Contrato')
    
    
class voucher(models.Model):
    _name = 'education_contract.voucher'
    
    date = fields.Date('Fecha')
    card_name = fields.Char('Nombre de tarjeta')  # revisar que sea un nomenclador
    voucher_number = fields.Char('Numero de voucher')
    auth_number = fields.Char('Numero de autorizacion')
    bank = fields.Many2one('res.bank', string='Banco')
    
    
    def name_get(self,cr,uid,ids,context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr,uid,ids,context)
        
        for object in record_name:
            res.append((object.id, '%s-%s %s' % (object.voucher_number, object.auth_number, object.bank.name)))
            
        return res
    
    
class check(models.Model):
    _name = 'education_contract.check'
    
    bank = fields.Many2one('res.bank', string='Banco')
    check_number = fields.Char('Numero de cheque')
    beneficiary = fields.Char('Beneficiario')
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr, uid, ids, context)
        
        for object in record_name:
            res.append((object.id, '%s-%s' % (object.check_number, object.bank.name)))
            
        return res
    
    
class transfer(models.Model):
    _name = 'education_contract.transfer'
    
    bank = fields.Many2one('res.bank', string='Banco')
    owner = fields.Char('Titular')
    auth_number = fields.Char('Numero de autorizacion')
    
    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context ={}
        res=[]
        
        record_name=self.browse(cr, uid, ids, context)
        
        for object in record_name:
            res.append((object.id, '%s-%s' % (object.owner, object.bank.name)))
            
        return res
    