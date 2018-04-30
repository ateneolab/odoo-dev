# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class CollectionPlan(models.Model):
    _name = 'collection_plan.collection_plan'

    @api.one
    @api.depends('active_plan_id', 'plan_ids', 'payment_term_ids')
    def _compute_payed_terms(self):
        pass

    @api.one
    @api.onchange('contract_id')
    @api.depends('contract_id')
    def onchange_contract_id(self):
        if self.contract_id:
            self.contract_id.write({'collection_id': self.id})

    @api.one
    def create_new_plan(self):
        if self.active_plan_id:
            self.active_plan_id.plan_active = False

        new_plan = self.active_plan_id.copy({
            'payment_term_ids': None,
            'amount_pay': self.active_plan_id.residual,
            'qty_dues': 0.0,
            'amount_monthly': self.active_plan_id.residual,
            'registration_fee': 0.0,
            'residual': self.active_plan_id.residual
        })

        self.plan_ids = [(4, self.active_plan_id.id)]
        self.active_plan_id = new_plan

    contract_id = fields.Many2one('education_contract.contract', string=_('Education contract'))
    active_plan_id = fields.Many2one('education_contract.plan')
    plan_ids = fields.One2many('education_contract.plan', 'collection_plan_id', string=_('Old plans'))
    residual = fields.Float(digits=(10, 4), string=_('Amount'))
    state = fields.Selection([('created', _('New')), ('done', _('Finish'))], default='created')
    payment_term_ids = fields.One2many(related='active_plan_id.payment_term_ids',
                                       string=_('Payment terms from active plan'))
    """payed_payment_term_ids = fields.One2many('education_contract.payment_term', 'payed_collection_plan_id',
                                         string=_('All payed Payment terms'), compute='_compute_payed_terms',
                                         store=True)"""
    user_id = fields.Many2one('res.users', string=_('Account manager'))
    start_date = fields.Date('Start date')
    end_date = fields.Date('End date')
    notes = fields.Text('Internal notes')


class EducationContractPlan(models.Model):
    _name = 'education_contract.plan'
    _inherit = 'education_contract.plan'

    collection_plan_id = fields.Many2one('collection_plan.collection_plan', string=_(''))
    plan_active = fields.Boolean(_('Active'))


class PaymentTerm(models.Model):
    _name = 'education_contract.payment_term'
    _inherit = 'education_contract.payment_term'

    planned_date = fields.Date(_('Planned date'))
    payment_date = fields.Date(_('Payment date'))
    payed = fields.Boolean(_('Payed?'))

    # payed_collection_plan_id = fields.One2many('collection_plan.collection_plan', string=_('Payed Collection Plan'))


class EducationContract(models.Model):
    _inherit = 'education_contract.contract'

    collection_id = fields.Many2one('collection_plan.collection_plan', string=_('Collection plan'))
