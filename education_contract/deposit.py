# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api
from datetime import datetime, timedelta
from dateutil import parser
from openerp.exceptions import ValidationError
from openerp.exceptions import except_orm, Warning, RedirectWarning


#### Conciliation
class conciliation(models.Model):
    _name = 'education_contract.conciliation'

    _rec_name = 'contract_id'

    seller_id = fields.Many2one('res.users', string='Vendedor')
    contract_id = fields.Many2one('education_contract.contract', string='Contrato')
    payment_term = fields.One2many('education_contract.payment_term', related='contract_id.payment_term_ids',
                                   string='Formas de pago')
    date = fields.Date('Fecha')

    """def name_search(self, cr, uid, name, args=None, operator='ilike', context=None, limit=100):
        if not args:
            args = []
        if not context:
            context = {}"""


#### Advance
class advance(models.Model):
    _name = 'education_contract.advance'

    seller_id = fields.Many2one('res.users', string='Vendedor')
    amount = fields.Float(digits=(6, 4), string='Monto', compute='_compute_amount', store=True)
    date = fields.Date('Fecha', required=False)
    base_payment_term_ids = fields.One2many('education_contract.payment_term', 'salary_advance_id',
                                            string='Abonos base', compute='_compute_amount', store=True)
    salary_advance_id = fields.Many2one('salary.advance', string='Avance de salario')
    journal_id = fields.Many2one('account.journal', string='Modo de pago')
    state = fields.Selection([('draft', 'Nuevo'), ('done', 'Generado'), ('cancel', 'Cancelado')], string='Estado',
                             default='draft')

    def _get_payment_term_to_advance(self):
        contract_ids = self.env['education_contract.contract'].search([('user_id', '=', self.seller_id.id)])
        plan_ids = self.env['education_contract.plan'].search([('contract_id', 'in', contract_ids.ids)])
        payment_term_ids = self.env['education_contract.payment_term'].search(
            [('plan_id', 'in', plan_ids.ids), ('state', 'in', ['to_advance'])])

        return payment_term_ids

    @api.depends('seller_id', 'date')
    def _compute_amount(self):
        payment_term_ids = self._get_payment_term_to_advance()

        sum = 0.0
        pt_ids = []

        for pt in payment_term_ids:
            sum += pt.amount

        self.amount = sum
        self.base_payment_term_ids = payment_term_ids.ids

    @api.one
    def generate_advance(self):

        employee_id = self.env['hr.employee'].search([('user_id', '=', self.seller_id.id)])

        if not employee_id:
            raise ValidationError("Debe configurar el empleado para el usuario %s." % self.seller_id)

        employee_obj = self.env['hr.employee'].browse(employee_id.ids)

        advance_data = {
            'advance': self.amount,
            'date': self.date,
            'employee_id': employee_obj.id,
            'payment_method': self.journal_id.id,
            'company_id': self.seller_id.company_id.id,
            'reason': 'Avance de vendedor',
            'is_seller_advance': True,
            'exceed_condition': True
        }

        advance_id = self.env['salary.advance'].create(advance_data)

        if advance_id:
            self.write({'salary_advance_id': advance_id.id})

            for pt in self.base_payment_term_ids:
                pt.write({'state': 'processed'})

        self.state = 'done'
