# -*- coding: utf-8 -*-

import datetime
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)

from openerp.exceptions import except_orm


class CollectionPlan(models.Model):
    _name = 'collection_plan.collection_plan'

    @api.multi
    def unlink(self):
        raise except_orm('Error', _(u"You can't remove a collection plan, you can only edit it."))

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

        payed = self.active_plan_id.get_payed()
        _logger.info('PAYED AFTER CALL plan.get_payed: %s' % payed)

        residual = self.active_plan_id.compute_residual()
        _logger.info('LOCAL RESIDUAL AFTER CALL compute_residual: %s' % residual)

        qty_dues = len(self.active_plan_id.payment_term_ids) - len(payed)
        _logger.info('QTY_DUES: %s' % qty_dues)

        new_plan = self.active_plan_id.copy({
            'payment_term_ids': None,
            'amount_pay': residual,
            'qty_dues': qty_dues,
            'amount_monthly': residual,
            'registration_fee': 0.0,  # habra que calcularlo de alguna forma?
            'residual': residual,
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

        self.active_plan_id.reschedule()

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

    @api.multi
    def get_payed(self):
        self.ensure_one()

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

    @api.multi
    def compute_residual(self):
        self.ensure_one()
        import pdb
        pdb.set_trace()
        residual = self.amount_pay
        for pt in self.payment_term_ids:
            if pt.payed:
                residual -= pt.amount

        return residual

    @api.one
    def reschedule(self):
        index = 1
        before_date = datetime.strptime(self.start_date, '%Y-%m-%d')

        self.remove_payment_terms()

        residual = self.compute_residual() if self.payment_term_ids else self.residual

        _logger.info('RESIDUAL ON RESCHEDULE: %s' % residual)
        amount_monthly = residual / (self.qty_dues or 1.0)

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
