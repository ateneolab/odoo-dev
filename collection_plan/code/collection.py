# -*- coding: utf-8 -*-

import datetime
from datetime import datetime

from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _


class CollectionPlan(models.Model):
    _name = 'collection_plan.collection_plan'

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []

        record_name = self.browse(cr, uid, ids, context)

        for object in record_name:
            res.append((object.id,
                        '%s-%s' % (object.contract_id.barcode or '', object.start_date or '')))

        return res

    @api.one
    def reschedule_plan(self):
        if self.active_plan_id:
            self.active_plan_id.start_date = self.start_date
            self.active_plan_id.reschedule()

    # @api.one
    # @api.depends('active_plan_id', 'plan_ids', 'payment_term_ids')
    # def _compute_payed_terms(self):
    #     pts = []
    #     for pt in self.active_plan_id.payment_term_ids:
    #         if pt.payed:
    #             pts.append(pt.id)
    #
    #     for pt_id in pts:
    #         self.payed_payment_term_ids = [(4, pt_id)]

    @api.one
    @api.onchange('contract_id')
    @api.depends('contract_id')
    def onchange_contract_id(self):
        if self.contract_id:
            self.contract_id.write({'collection_id': self.id})

    @api.one
    @api.onchange('active_plan_id')
    @api.depends('active_plan_id')
    def onchange_active_plan_id(self):
        if self.active_plan_id:
            self.active_plan_id.write({'collection_plan_id': self.id})

    @api.one
    def create_new_plan(self):
        if self.active_plan_id:
            self.active_plan_id.plan_active = False

        import pdb
        pdb.set_trace()

        payed = self.active_plan_id.get_payed()

        new_plan = self.active_plan_id.copy({
            'payment_term_ids': None,
            'amount_pay': self.active_plan_id.residual,  # el total a pagar es lo que no se ha pagado hasta el momento
            'qty_dues': 0.0,
            'amount_monthly': self.active_plan_id.residual,
            'registration_fee': 0.0,
            'residual': self.active_plan_id.residual,
            'collection_plan_id': self.id,
            'plan_active': True,
            'contract_id': None,
        })
        self.env.cr.commit()

        self.plan_ids = [(4, self.active_plan_id.id)]
        self.active_plan_id = new_plan

        for pt in payed:
            self.write({
                'payed_payment_term_ids': [(4, pt.id)]
            })

    contract_id = fields.Many2one('education_contract.contract', string=_('Education contract'))
    active_plan_id = fields.Many2one('education_contract.plan')
    plan_ids = fields.One2many('education_contract.plan', 'collection_plan_id', string=_('Old plans'))
    residual = fields.Float(digits=(10, 4), string=_('Amount'))
    state = fields.Selection([('created', _('New')), ('done', _('Finish'))], default='created')
    payment_term_ids = fields.One2many(related='active_plan_id.payment_term_fixed_ids',
                                       string=_('Payment terms from active plan'))
    payed_payment_term_ids = fields.One2many('education_contract.payment_term', 'payed_collection_plan_id',
                                             string=_('All payed Payment terms'), store=True)

    user_id = fields.Many2one('res.users', string=_('Account manager'))
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    notes = fields.Text('Internal notes')


class EducationContractPlan(models.Model):
    _name = 'education_contract.plan'
    _inherit = 'education_contract.plan'

    @api.one
    def get_payed(self):
        payed = []
        for pt in self.payment_term_ids:
            if pt.payed:
                payed.append(pt)
        return payed

    @api.one
    def remove_payment_terms(self):
        for pt in self.payment_term_fixed_ids:
            if not pt.payed:
                pt.unlink()

        for pt in self.payment_term_ids:
            if not pt.payed:
                pt.unlink()

    @api.one
    def compute_residual(self):
        residual = 0.0
        import pdb
        pdb.set_trace()
        for pt in self.payment_term_ids:
            if not pt.payed:
                residual += pt.amount

        self.write({
            'residual': residual
        })

    @api.one
    def reschedule(self):
        index = 1
        before_date = datetime.strptime(self.start_date, '%Y-%m-%d')

        self.remove_payment_terms()

        self.compute_residual()

        import pdb
        pdb.set_trace()

        amount_monthly = self.residual / (self.qty_dues or 1)

        if self.qty_dues and self.plan_active:
            for n in range(1, self.qty_dues + 1):
                if index == 1:
                    sd = before_date
                else:
                    sd = before_date + relativedelta(months=+1)

                new_payment_term = self.env['education_contract.payment_term'].create({
                    'amount': amount_monthly,
                    'planned_date': sd,
                    'plan_id': self.id
                })

                self.payment_term_fixed_ids = [(4, new_payment_term.id)]

                before_date = sd

                index += 1

    @api.one
    @api.onchange('payment_term_ids')
    def _compute_balance(self):
        print('COMPUTE BALANCE')
        sum = 0.0
        if self.payment_term_ids:
            for pt in self.payment_term_ids:
                if not pt.payed:
                    sum += pt.amount
        self.balance = sum

    """@api.one
    @api.depends('qty_dues')
    def _compute_payment_terms(self):
        import pdb;
        pdb.set_trace()
        print('COMPUTE PAYMENT TERMS')
        index = 1
        before_date = datetime.date.today()

        if self.qty_dues and self.collection_plan_id \
                and self.amount_monthly \
                and self.plan_active \
                and not self.payment_term_fixed_ids:
            for n in range(1, self.qty_dues + 1):
                if index == 1:
                    sd = before_date
                else:
                    sd = before_date + relativedelta(months=+1)

                new_payment_term = self.env['education_contract.payment_term'].create({
                    'amount': self.amount_monthly,
                    'planned_date': sd,
                    'plan_id': self.id
                })

                self.payment_term_fixed_ids = [(4, new_payment_term)]

                before_date = sd"""

    payment_term_fixed_ids = fields.One2many('education_contract.payment_term', 'fixed_plan_id',
                                             string=_('Payment terms'))
    collection_plan_id = fields.Many2one('collection_plan.collection_plan', string=_(''))
    plan_active = fields.Boolean(_('Active'))
    balance = fields.Float(digits=(6, 4), compute='_compute_balance', string=_('Balance'))
    start_date = fields.Date(_('Start date'))


class PaymentTerm(models.Model):
    _name = 'education_contract.payment_term'
    _inherit = 'education_contract.payment_term'

    planned_date = fields.Date(_('Planned date'))
    payment_date = fields.Date(_('Payment date'))
    payed = fields.Boolean(_('Payed?'))
    order = fields.Integer('Order')
    fixed_plan_id = fields.Many2one('education_contract.plan', string=_('Payment Plan'))
    payed_collection_plan_id = fields.Many2one('collection_plan.collection_plan', string=_('Payed Collection Plan'))


class EducationContract(models.Model):
    _inherit = 'education_contract.contract'

    collection_id = fields.Many2one('collection_plan.collection_plan', string=_('Collection plan'))
