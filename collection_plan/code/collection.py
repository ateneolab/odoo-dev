# -*- coding: utf-8 -*-

import datetime
import logging
from itertools import chain
from datetime import datetime

from dateutil.relativedelta import relativedelta

from openerp import models, fields, api, _

_logger = logging.getLogger(__name__)

from openerp.exceptions import except_orm
from openerp.exceptions import ValidationError


class CollectionPlan(models.Model):
    _name = "collection_plan.collection_plan"

    @api.multi
    def unlink(self):
        raise except_orm(
            "Error", _(u"You can't remove a collection plan, you can only edit it.")
        )

    def name_get(self, cr, uid, ids, context=None):
        if context is None:
            context = {}
        res = []

        record_name = self.browse(cr, uid, ids, context)

        for object in record_name:
            res.append(
                (
                    object.id,
                    "%s-%s"
                    % (object.contract_id.barcode or "", object.start_date or ""),
                )
            )

        return res

    @api.one
    def reschedule_plan(self):
        if self.active_plan_id:
            self.active_plan_id.start_date = self.start_date
            self.active_plan_id.reschedule()

    @api.one
    @api.onchange("contract_id")
    @api.depends("contract_id")
    def onchange_contract_id(self):
        if self.contract_id:
            self.contract_id.write({"collection_id": self.id})

    @api.one
    @api.onchange("active_plan_id")
    @api.depends("active_plan_id")
    def onchange_active_plan_id(self):
        if self.active_plan_id:
            self.active_plan_id.write({"collection_plan_id": self.id})

    @api.one
    def create_new_plan(self):
        if self.active_plan_id:
            self.active_plan_id.plan_active = False

        payed = self.active_plan_id.get_payed()
        _logger.info("PAYED AFTER CALL plan.get_payed: %s" % payed)

        residual = self.active_plan_id.compute_residual()
        _logger.info("LOCAL RESIDUAL AFTER CALL compute_residual: %s" % residual)

        qty_dues = len(self.active_plan_id.payment_term_ids) - len(payed)
        _logger.info("QTY_DUES: %s" % qty_dues)

        new_plan = self.active_plan_id.copy(
            {
                "payment_term_ids": None,
                "amount_pay": residual,
                "qty_dues": qty_dues,
                "amount_monthly": residual,
                "registration_fee": 0.0,  # habra que calcularlo de alguna forma?
                "residual": residual,
                "collection_plan_id": self.id,
                "plan_active": True,
                "contract_id": None,
            }
        )
        self.env.cr.commit()

        self.plan_ids = [(4, self.active_plan_id.id)]
        self.active_plan_id = new_plan

        for pt in payed:
            self.write({"payed_payment_term_ids": [(4, pt.id)]})

        self.active_plan_id.reschedule()

    @api.one
    def update_payed(self):
        payed = self.active_plan_id.get_payed()
        for pt in payed:
            self.write({"payed_payment_term_ids": [(4, pt.id)]})

    @api.multi
    def generate_invoice(self):
        self.update_payed()
        collection_id = self._context.get("collection_plan_id", None)
        wizard_form = self.env.ref("collection_plan.view_wizard_invoice_form", False)
        view_id = self.env["collection_plan.wizard_invoice"]
        new = view_id.create({})
        return {
            "name": _("Generar factura"),
            "type": "ir.actions.act_window",
            "res_model": "collection_plan.wizard_invoice",
            "res_id": new.id,
            "view_id": wizard_form.id,
            "view_mode": "form",
            "view_type": "form",
            "nodestroy": True,
            "target": "new",
            "context": {"collection_plan_id": collection_id},
        }

    contract_id = fields.Many2one(
        "education_contract.contract", string=_(u"Contrato de educación")
    )
    active_plan_id = fields.Many2one(
        "education_contract.plan", string=_(u"Plan activo")
    )
    plan_ids = fields.One2many(
        "education_contract.plan", "collection_plan_id", string=_("Old plans")
    )
    residual = fields.Float(
        digits=(10, 4), string=_(u"Cantidad"), compute="_compute_residual", store=True
    )
    balance = fields.Float(
        digits=(6, 4), string=_("Balance"), compute="_compute_balance", store=True
    )
    state = fields.Selection(
        [("created", _("New")), ("done", _("Finish"))], default="created"
    )
    payment_term_ids = fields.One2many(
        "education_contract.payment_term",
        "collection_plan_id",
        related="active_plan_id.payment_term_fixed_ids",
        string=_(u"Información de pago"),
    )
    payed_payment_term_ids = fields.One2many(
        "education_contract.payment_term",
        "payed_collection_plan_id",
        string=_("Formas de pago pagadas"),
        store=True,
    )
    user_id = fields.Many2one("res.users", string=_(u"Gerente de cuenta"))
    start_date = fields.Date(_(u"Fecha de inicio"))
    end_date = fields.Date(_(u"Fecha de fin"))
    notes = fields.Text(_(u"Notas internas"))
    invoice_ids = fields.Many2many("account.invoice", string=_(u"Facturas"))
    account_number = fields.Char("No. de cuenta", readonly=True)
    barcode = fields.Char(
        related="contract_id.barcode", string=_(u"Código de contrato")
    )
    state = fields.Selection(
        [
            ("new", _(u"Nuevo")),
            ("cancelled_parcial", _(u"Cancelado parcial")),
            ("cancelled", _(u"Cancelado")),
            ("frozen", _(u"Congelado")),
            ("retired", _(u"Retirado")),
        ],
        default="new",
        store=True,
    )
    campus_id = fields.Many2one(related="contract_id.campus_id")
    freezing_ids = fields.One2many(
        "collection.plan.freeze", "collection_plan_id", string=_(u"Congelamientos")
    )
    retired_ids = fields.One2many(
        "collection.plan.retired", "collection_plan_id", string=_(u"Retirado")
    )

    @api.multi
    def do_retired(self):
        self.check_state_retired_frozen()
        self.retired_roll_number()
        self.write({"state": "retired"})

    @api.multi
    def do_frozen(self):
        self.check_state_retired_frozen()
        return self.generated_frozen()

    @api.multi
    def do_re_enter_frozen(self):
        """Para reingresar las cobranza en estado congelado

        """
        self.update_date_re_enter(is_frozen=True)
        self.change_state_collection_plan()

    def do_re_enter_roll_number(self, date):
        """Actualiza la fecha de reingreso de las matriculas
        cuando la cobranza se reingresa.
        """
        roll_numbers = self.contract_id.roll_number_ids
        for record in roll_numbers:
            frozen_collection = record.freezing_ids.filtered(
                lambda item: item.is_collection
            )
            if frozen_collection:
                frozen = frozen_collection.sorted(
                    key=lambda r: r.create_date, reverse=False
                )[-1]
                frozen.write({"end_date": date})

    def update_date_re_enter(self, is_frozen=False):
        """Reingresa las cobranza tanto en estado congelado como retirado

        """
        today = datetime.today()
        if is_frozen and self.freezing_ids:
            self.do_re_enter_roll_number(today)
            frozen = self.freezing_ids.sorted(
                key=lambda r: r.create_date, reverse=False
            )[-1]
            frozen.write({"end_date": today})
        if not is_frozen and self.retired_ids:
            retired = self.retired_ids.sorted(
                key=lambda r: r.create_date, reverse=False
            )[-1]
            retired.write({"end_date": today})

    @api.multi
    def do_re_enter(self):
        """Reintegra las cobranzas en estado retirado

        """
        self.update_date_re_enter(is_frozen=False)
        roll_numbers = self.contract_id.roll_number_ids
        roll_numbers.write({"state": "active"})
        self.change_state_collection_plan()

    def retired_roll_number(self):
        """Pone las mátriculas y las cobranzas en estado retirado.
        """
        roll_numbers = self.contract_id.roll_number_ids
        roll_numbers.write({"state": "gone"})
        Retired = self.env["collection.plan.retired"]
        Retired.create(
            dict(retired_date=datetime.now().date(), collection_plan_id=self.id)
        )

    def check_state_retired_frozen(self):
        """Chequea que no existan pagos sin pagar en el mes en curso. Para
        cambiar de estado la cobranza.

        """
        today = datetime.now().date()
        res = []
        payments = self.payment_term_ids.filtered(
            lambda item: not item.payed and not item.invoice_id
        )
        for payed in payments:
            planned_date = datetime.strptime(payed.planned_date, "%Y-%m-%d").date()
            if planned_date.month == today.month and planned_date.year == today.year:
                res.append(payed)
        if res:
            raise ValidationError(
                "No se puede cambiar de estado mientras existan pagos sin pagar en el mes en curso."
            )

    @api.model
    def re_plan_collections(self):
        domain = [("state", "=", "frozen")]
        collections = self.search(domain)
        today = datetime.today()
        for record in collections:
            freezing = record.freezing_ids.sorted(
                key=lambda r: r.create_date, reverse=False
            )[-1]
            if freezing:
                if datetime.strptime(freezing.end_date, "%Y-%m-%d") < today:
                    record.re_plan_payments(today)
                    freezing.end_date = today
                    record.change_state_collection_plan()
                    record.do_re_enter_roll_number(today)

    def re_plan_payments(self, date):
        """Replanifica todas las cuotas a partir de la fecha de hoy
        """
        payments = self.payment_term_ids.filtered(lambda item: not item.payed)
        if payments:
            payments = chain(payments)
            payment = next(payments, None)
            while payment:
                payment.planned_date = date
                date = date + relativedelta(months=1)
                payment = next(payments, None)

    def generated_frozen(self):
        collection_id = self._context.get("default_collection_plan_id", None)
        contract_id = self._context.get("default_contract_id", None)
        view_id = self.env.ref("collection_plan.view_wizard_frozen_form")
        new = self.env["collection_plan.wizard_frozen"].create({})
        return {
            "name": _("Congelar cobranza"),
            "type": "ir.actions.act_window",
            "res_model": "collection_plan.wizard_frozen",
            "res_id": new.id,
            "view_id": view_id.id,
            "view_mode": "form",
            "view_type": "form",
            "nodestroy": True,
            "target": "new",
            "context": {
                "default_collection_plan_id": collection_id,
                "default_contract_id": contract_id,
            },
        }

    def change_state_collection_plan(self):
        """Obtiene el estado de las cobranzas
        """
        if self.payment_term_ids:
            if all(item.payed for item in self.payment_term_ids):
                self.state = "cancelled"
            if any(not item.payed for item in self.payment_term_ids):
                self.state = "cancelled_parcial"
            if all(not item.payed for item in self.payment_term_ids):
                self.state = "new"

    def _compute_account_number(self):
        sequence = self._get_sequence()
        account_number = u"{}-{}".format(str(self.contract_id.barcode), str(sequence))
        self.account_number = account_number

    def _get_sequence(self):
        context = {}
        cr = self._cr
        uid = self._context.get("uid")
        ids = self.campus_id.ir_sequence.id
        return self.pool.get("ir.sequence").next_by_id(cr, uid, ids, context)

    @api.one
    @api.depends("active_plan_id", "payment_term_ids")
    def _compute_residual(self):
        for rec in self:
            plan_id = rec.active_plan_id
            residual = plan_id.compute_residual()
            rec.residual = residual

    @api.depends(
        "payment_term_ids",
        "payment_term_ids.amount_paid",
        "payment_term_ids.invoice_id",
    )
    def _compute_balance(self):
        """Total de las cuotas planificadas que faltan por pagar
        """
        for record in self:
            record.balance = sum(
                item.amount_paid for item in record.payment_term_ids if not item.payed
            )

    @api.model
    def create(self, vals):
        res = super(CollectionPlan, self).create(vals)
        res.update_order_payment(values=vals)
        res._compute_account_number()
        verification = vals.get("verification_id")
        if not verification:
            res.change_state_collection_plan()
        return res

    @api.multi
    def write(self, vals):
        if "user_id" in vals or "active_plan_id" in vals:
            if not self.env.user.has_group(
                "collection_plan.group_admin_collection_plan"
            ):
                raise except_orm(
                    "Error de acceso",
                    u"Solo tiene permitido confirmar los pagos. No puede modificar otros datos.",
                )
        res = super(CollectionPlan, self).write(vals)
        self.update_order_payment(values=vals)
        if "payment_term_ids" in vals:
            self.change_state_collection_plan()
        return res

    def update_order_payment(self, values=None):
        self._update_order_payment()
        return True

    def _update_order_payment(self):
        payments = self.payment_term_ids
        order_payments = payments.sorted(key=lambda r: r.planned_date, reverse=False)
        count = 1
        for item in order_payments:
            item.order = count
            count = count + 1


class EducationContractPlan(models.Model):
    _name = "education_contract.plan"
    _inherit = "education_contract.plan"

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

        residual = self.amount_pay
        for pt in self.payment_term_ids:
            if pt.invoice_id or pt.voucher_id or pt.payed:
                residual -= pt.amount

        return residual

    @api.one
    def reschedule(self):
        index = 1
        before_date = datetime.strptime(self.start_date, "%Y-%m-%d")

        self.remove_payment_terms()

        residual = self.compute_residual() if self.payment_term_ids else self.residual

        qty_dues = self.qty_dues - len(self.payment_term_ids)
        _logger.info("COMPUTED QTY_DUES: %s" % qty_dues)

        _logger.info("RESIDUAL ON RESCHEDULE: %s" % residual)
        # amount_monthly = residual / (qty_dues or 1.0)
        amount_monthly = residual / (self.qty_dues or 1.0)

        if self.qty_dues and self.plan_active:
            for n in range(1, self.qty_dues + 1):
                if index == 1:
                    sd = before_date
                else:
                    sd = before_date + relativedelta(months=+1)

                new_payment_term = self.env["education_contract.payment_term"].create(
                    {
                        "amount": amount_monthly,
                        "planned_date": sd,
                        "plan_id": self.id,
                        "collection_plan_id": self.collection_plan_id.id,
                    }
                )

                self.payment_term_fixed_ids = [(4, new_payment_term.id)]
                before_date = sd
                index += 1

    payment_term_fixed_ids = fields.One2many(
        "education_contract.payment_term",
        "fixed_plan_id",
        string=_("Información de pago"),
    )
    collection_plan_id = fields.Many2one(
        "collection_plan.collection_plan", string=_("")
    )
    plan_active = fields.Boolean(_("Active"))
    balance = fields.Float(digits=(6, 4), string=_("Balance"))
    start_date = fields.Date(_("Start date"))
    qty_payment = fields.Integer(
        string=_(u"Cantidad de pagos"), compute="_compute_qty_payment"
    )

    @api.depends("payment_term_fixed_ids")
    def _compute_qty_payment(self):
        for record in self:
            qty = len(record.payment_term_fixed_ids)
            record.qty_payment = qty


class PaymentTerm(models.Model):
    _name = "education_contract.payment_term"
    _inherit = "education_contract.payment_term"
    _order = "planned_date,payment_date"

    planned_date = fields.Date(_(u"Fecha planificada"))
    payment_date = fields.Date(_(u"Fecha de pago"))
    payed = fields.Boolean(_(u"Pagado?"))
    order = fields.Integer(string=_(u"Order"))
    fixed_plan_id = fields.Many2one(
        "education_contract.plan", string=_(u"Plan de pago")
    )
    payed_collection_plan_id = fields.Many2one(
        "collection_plan.collection_plan", string=_(u"Plan de pago de cobranza")
    )
    collection_plan_id = fields.Many2one(
        "collection_plan.collection_plan", string=_(u"Plan de cobranza")
    )


class EducationContract(models.Model):
    _inherit = "education_contract.contract"

    collection_id = fields.Many2one(
        "collection_plan.collection_plan", string=_("Collection plan")
    )


class Freeze(models.Model):
    _name = "collection.plan.freeze"

    start_date = fields.Date(u"Fecha de inicio")
    end_date = fields.Date(u"Fecha reingreso")
    duration = fields.Integer(u"Duración en meses")
    collection_plan_id = fields.Many2one("collection_plan.collection_plan", u"Cobranza")


class Retired(models.Model):
    _name = "collection.plan.retired"

    retired_date = fields.Date(u"Fecha de retirado")
    end_date = fields.Date(u"Fecha reingreso")
    collection_plan_id = fields.Many2one("collection_plan.collection_plan", u"Cobranza")
