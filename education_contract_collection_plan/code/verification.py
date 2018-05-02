# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api, _


class ContractVerification(models.Model):
    _name = 'education_contract.verification'

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
            'start_date': plan_id.start_date
        })

    operating_unit_id = fields.Many2one(related='contract_id.campus_id')
    contract_id = fields.Many2one('education_contract.contract', _('Education contract'))
    contract_date = fields.Date(_('Contract date'), related='contract_id.date')
    verification_date = fields.Date()
    agreement_duration = fields.Integer(_('Duration of the agreement (Months)'))
    verification_place = fields.Selection([('office', _('Office')), ('home', _('Home')), ('work', _('Work'))],
                                          default='home')
    user_id = fields.Many2one(related='contract_id.seller_id')
    collection_plan_id = fields.Many2one('collection_plan.collection_plan', _('Collection plan'))
    plan_id = fields.Many2one('education_contract.plan', _('Payment plan'))
    payment_term_ids = fields.One2many(related='plan_id.payment_term_ids')


class CollectionPlan(models.Model):
    _inherit = 'collection_plan.collection_plan'

    verification_id = fields.Many2one('education_contract.verification', 'collection_plan_id')

    """@api.one
    def generate_verification(self):
        verification_id = self.env['education_contract.verification'].create({
            'collection_plan_id': self.id,
            'contract_id': self.contract_id.id,
        })

        self.write({
            'verification_id': verification_id.id
        })"""
