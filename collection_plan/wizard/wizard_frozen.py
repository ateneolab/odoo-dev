# -*- coding: utf-8 -*-

from datetime import datetime
import logging
from dateutil.relativedelta import relativedelta
from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)


class WizardFrozen(models.TransientModel):
    _name = "collection_plan.wizard_frozen"

    @api.model
    def _default_contract_id(self):
        return self._context.get("default_contract_id", None)

    @api.model
    def _default_collection_id(self):
        return self._context.get("default_collection_plan_id", None)

    @api.model
    def _default_payment_id(self):
        return self._context.get("default_id", None)

    @api.model
    def _default_invoice_id(self):
        return self._context.get("default_invoice_id", None)

    contract_id = fields.Many2one(
        "education_contract.contract", "Contrato", default=_default_contract_id
    )
    collection_plan_id = fields.Many2one(
        "collection_plan.collection_plan", default=_default_collection_id
    )

    start_date = fields.Date(u"Fecha de inicio")
    end_date = fields.Date(u"Fecha reingreso")
    duration = fields.Integer(
        u"Duración en meses", compute="_compute_duration", inverse="_set_duration"
    )

    @api.depends("start_date", "end_date")
    def _compute_duration(self):
        if self.start_date and self.end_date:
            start_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(self.end_date, "%Y-%m-%d")
            self.duration = end_date.month - start_date.month
        else:
            self.duration = 0

    def _set_duration(self):
        if self.start_date:
            before_date = datetime.strptime(self.start_date, "%Y-%m-%d")
            self.end_date = before_date + relativedelta(months=self.duration)
        else:
            self.end_date = False

    @api.multi
    def create_frozen(self):
        roll_numbers = self.contract_id.roll_number_ids
        roll_numbers.write({"frozen": True})
        self.collection_plan_id.write({"state": "frozen"})
        vals = {
            "start_date": self.start_date,
            "duration": self.duration,
            "end_date": self.end_date,
            "collection_plan_id": self.collection_plan_id.id,
        }
        Frozen = self.env["collection.plan.freeze"]
        Frozen.create(vals)
