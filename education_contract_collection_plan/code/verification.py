# -*- coding: iso-8859-1 -*-

from openerp import models, fields, api, _
from datetime import datetime, timedelta
from openerp.exceptions import ValidationError


class ContractVerification(models.Model):
    _name = 'education_contract.verification'

    operating_unit_id = fields.Many2one('operating.unit', 'verification_id', string=_('Branch Office'),
                                        related='contract_id.campus_id')
    contract_id = fields.Many2one('education_contract.contract', string=_('Contract'))
    contract_date = fields.Date(_('Contract date'), related='contract_id.date')
    verification_date = fields.Date()
    agreement_duration = fields.Integer(_('Duration of the agreement (Months)'))
    verification_place = fields.Selection([('office', _('Office')), ('home', _('Home')), ('work', _('Work'))],
                                          default='home')
    user_id = fields.Many2one('res.users', 'verification_id', string=_('Verified by'), related='contract_id.seller_id')
    collection_plan_id = fields.Many2one('collection_plan.collection_plan')


class BranchOffice(models.Model):
    _name = 'operating.unit'
    _inherit = 'operating.unit'

    verification_id = fields.One2many('education_contract.verification')


class Contract(models.Model):
    _inherit = 'education_contract.contract'

    verification_id = fields.Many2one('education_contract.verification')


class User(models.Model):
    _inherit = 'res.users'

    verification_id = fields.Many2one('education_contract.verification')


class CollectionPlan(models.Model):
    _inherit = 'collection_plan.collection_plan'

    verification_id = fields.Many2one('education_contract.verification')

    @api.one
    def generate_verification(self):
        verification_id = self.env['education_contract.verification'].create({
            'collection_plan_id': self.id,
            'contract_id': self.contract_id.id,
        })

        self.write({
            'verification_id': verification_id.id
        })
