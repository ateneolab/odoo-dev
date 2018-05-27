# -*- coding: utf-8 -*-

import datetime
import logging

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

_logger = logging.getLogger(__name__)


class WizardInvoice(models.TransientModel):
    _name = 'collection_plan.wizard_invoice'
    _inherit = 'collection_plan.wizard_invoice'

    verification_id = fields.Many2one('education_contract.verification', related='contract_id.verification_id')
    collection_plan_id = fields.Many2one('collection_plan.collection_plan',
                                         related='verification_id.collection_plan_id')

