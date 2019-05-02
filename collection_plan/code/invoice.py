# -*- coding: utf-8 -*-

import datetime
import logging
from datetime import datetime

from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)

from openerp.exceptions import except_orm


class Invoice(models.Model):
    _name = 'education_contract.payment_term'
    _inherit = 'education_contract.payment_term'

    invoice_id = fields.Many2one('account.invoice', string=_('Invoice'))
