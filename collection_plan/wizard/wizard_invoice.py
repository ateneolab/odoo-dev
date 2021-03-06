# -*- coding: utf-8 -*-

import datetime
import logging

from openerp import models, fields, api, _
from openerp.exceptions import except_orm

_logger = logging.getLogger(__name__)


class WizardInvoice(models.TransientModel):
    _name = "collection_plan.wizard_invoice"

    @api.model
    def _default_contract_id(self):
        return self._context.get("default_contract_id", None)

    @api.model
    def _default_collection_id(self):
        return self._context.get("collection_plan_id", None)

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

    @api.model
    def default_get(self, fields):
        Payment = self.env["education_contract.payment_term"]
        res = super(WizardInvoice, self).default_get(fields)
        collection_plan_id = self._context.get("collection_plan_id", None)
        invoice_id = res.get("invoice_id")
        if "payment_term_ids" in fields:
            if res.get("payment_id"):
                payment_id = res.get("payment_id")
                domain = [("id", "=", payment_id)]
                payment = Payment.search(domain)
            else:
                domain = [
                    ("payed_collection_plan_id", "=", collection_plan_id),
                    ("invoice_id", "=", invoice_id),
                ]
                payment = Payment.search(domain)
            res.update({"payment_term_ids": payment.ids})
        return res

    payment_id = fields.Many2one(
        "education_contract.payment_term",
        string=_(u"Pago"),
        default=_default_payment_id,
    )

    invoice_id = fields.Many2one(
        "account.invoice", string=_(u"Invoices"), default=_default_invoice_id
    )
    payment_term_ids = fields.Many2many(
        "education_contract.payment_term",
        "wizard_invoice_payment_term",
        string=_("Payments"),
    )
    partner_id = fields.Many2one(
        "res.partner", related="contract_id.owner", string=_("Customer")
    )
    operating_unit_id = fields.Many2one(
        "operating.unit", related="contract_id.campus_id", string=_("Branch office")
    )
    company_id = fields.Many2one(
        related="operating_unit_id.company_id", string=_(u"Company")
    )

    @api.multi
    def build_lines(self):
        self.ensure_one()
        inv_lines = []

        for payment in self.payment_term_ids:
            if payment.description:
                name = payment.description
            else:
                name = "Contrato: %s - Fecha de pago: %s" % (
                    payment.plan_id.collection_plan_id.contract_id.barcode,
                    payment.payment_date,
                )

            default_product_id = self.env["product.template"].search(
                [("name", "=", "IMPORT SRI PRODUCT")]
            )
            default_product = self.env["product.product"].search(
                [("product_tmpl_id", "=", default_product_id.id)]
            )

            cm_product_template_util_id = default_product_id.product_template_util_id
            if not cm_product_template_util_id:
                raise _(
                    "Accounts for default product is not set correctly for multi company."
                )

            account = cm_product_template_util_id.account_income
            _logger.info("account_income: %s" % str(account))

            account = (
                self.env["account.account"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", self.operating_unit_id.company_id.id),
                        ("code", "=", account.code),
                    ]
                )
            )
            _logger.info("account_income from company: %s" % str(account))

            # t_domain = [
            #     ('porcentaje', '=', '0'),  # cable, se deberia tomar por parametro, igual se puede editar luego
            #     ('tax_group', '=', 'vat0'),  # cable, se deberia tomar por parametro, igual se puede editar luego
            #     ('company_id', '=', self.operating_unit_id.company_id.id),
            #     ('type_tax_use', 'in', ['sale', 'all'])]
            # tax_id = self.env['account.tax'].search(t_domain)[:1]

            line = {
                "name": name,
                "account_id": account.id,
                "price_unit": payment.amount,
                "quantity": float(1.0),
                "product_id": default_product.id,
                "invoice_line_tax_id": payment.tax_ids.ids,
                "account_analytic_id": False,
            }

            inv_lines.append((0, 0, line))

        return inv_lines

    @api.multi
    def build_invoice_data(self, inv_lines):
        company_id = self.operating_unit_id.company_id

        receivable_account_id = company_id.partner_id.property_account_receivable
        if not receivable_account_id:
            raise Exception(_("Payable account for company is not set correctly"))

        if receivable_account_id.company_id.id != company_id:
            receivable_account_id = (
                self.env["account.account"]
                .sudo()
                .search(
                    [
                        ("code", "=", receivable_account_id.code),
                        ("company_id", "=", company_id.id),
                    ]
                )
            )

        currency_id = self.env["res.currency"].search([("name", "=", "USD")])[:1]

        fpos = self.partner_id.property_account_position
        if not fpos:
            raise Exception(
                _(
                    u"Fiscal position is not configured por partner: %s"
                    % self.partner_id.ced_ruc
                )
            )

        inv_date = datetime.date.today()

        period_id = self.get_period(company_id.id, inv_date.strftime("%d/%m/%Y"))
        _logger.info("period: %s" % period_id)

        auth_id = self.env["account.authorisation"].search(
            [
                ("operating_unit_id", "=", self.operating_unit_id.id),
                ("type_id.code", "=", "18"),
            ]
        )
        if not auth_id:
            raise Exception(_(u"authorization document is not configured."))
        for _id, _cod, dic_line in inv_lines:
            if "payment_id" in dic_line:
                Payment = self.env["education_contract.payment_term"]
                payment = Payment.browse(dic_line["payment_id"])
                if payment.discount_type == "percentage":
                    discount_type = "percent"
                    discount_scope = "per_line_before_tax"
                elif payment.discount_type == "fixed_amount":
                    discount_type = "amount"
                    discount_scope = "per_line_before_tax"
                elif not payment.discount_type:
                    discount_type = ""
                    discount_scope = "total_before_tax"

        inv_data = {
            "name": "Factura generada",
            "origin": "Cobranzas",
            "type": "out_invoice",
            "reference": False,
            "account_id": receivable_account_id.id,
            "partner_id": self.partner_id.id,
            "discount_scope": discount_scope,
            "discount_type": discount_type,
            "invoice_line": inv_lines,
            "currency_id": currency_id.id,
            "comment": "",
            "payment_term": 1,  # CABLE POR AHORA, HAY QUE OBTENERLO
            "fiscal_position": fpos.id,
            "date_invoice": inv_date,
            "date_due": inv_date,
            "company_id": self.company_id.id,
            "period_id": period_id.id,
            "operating_unit_id": self.operating_unit_id.id,
            "auth_inv_id": auth_id.id,
        }

        return inv_data

    @api.multi
    def get_period(self, company_id, date_str, context=None):
        code = "%s/%s" % (date_str[3:5], date_str[6:])
        domain = [("code", "=", code), ("company_id", "=", company_id)]
        period_id = self.env["account.period"].search(domain)[:1]
        return period_id

    @api.multi
    def open_invoices(self, invoice_id):
        """ open a view on one of the given invoice_ids """
        ir_model_data = self.pool.get("ir.model.data")
        form_res = ir_model_data.get_object_reference(
            self._cr, self._uid, "account", "invoice_form"
        )
        form_id = form_res and form_res[1] or False
        tree_res = ir_model_data.get_object_reference(
            self._cr, self._uid, "account", "invoice_tree"
        )
        tree_id = tree_res and tree_res[1] or False

        return {
            "name": _("Generated Invoice"),
            "view_type": "form",
            "view_mode": "form,tree",
            "res_model": "account.invoice",
            "res_id": invoice_id,
            "view_id": False,
            "views": [(form_id, "form"), (tree_id, "tree")],
            "context": "{'type': 'out_invoice'}",
            "type": "ir.actions.act_window",
        }

    @api.multi
    def create_individual_invoice(self):
        inv_obj = self.env["account.invoice"]
        inv_lines = []

        for payment in self.payment_term_ids:
            if payment.description:
                name = payment.description
            else:
                name = "Contrato: %s - Fecha de pago: %s" % (
                    payment.plan_id.collection_plan_id.contract_id.barcode,
                    payment.payment_date,
                )

            default_product_id = self.env["product.template"].search(
                [("name", "=", "IMPORT SRI PRODUCT")]
            )
            default_product = self.env["product.product"].search(
                [("product_tmpl_id", "=", default_product_id.id)]
            )

            cm_product_template_util_id = default_product_id.product_template_util_id
            if not cm_product_template_util_id:
                raise _(
                    "Accounts for default product is not set correctly for multi company."
                )

            account = cm_product_template_util_id.account_income
            _logger.info("account_income: %s" % str(account))

            account = (
                self.env["account.account"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", self.operating_unit_id.company_id.id),
                        ("code", "=", account.code),
                    ]
                )
            )
            _logger.info("account_income from company: %s" % str(account))
            line = {
                "name": name,
                "account_id": account.id,
                "price_unit": payment.amount,
                "discount": payment.discount,
                "discount_amount": payment.discount,
                "quantity": float(1.0),
                "product_id": default_product.id,
                "account_analytic_id": False,
                "payment_id": payment.id,
            }

            if not self.taxes_included or not payment.taxes_included:
                line.update({"invoice_line_tax_id": [(6, 0, payment.tax_ids.ids)]})

            inv_lines.append((0, 0, line))

        _logger.info("INV_LINES: %s" % inv_lines)

        inv_data = self.build_invoice_data(inv_lines)
        _logger.info("INV_DATA: %s" % inv_data)

        inv = inv_obj.create(inv_data)
        _logger.info("INV: %s" % inv)
        inv.button_reset_taxes()
        inv.signal_workflow("invoice_open")

        self.reconcile_payments(inv, self.taxes_included)
        _logger.info("RECONCILE PAYMENTS...")

        for pt in self.payment_term_ids:
            pt.write({"invoice_id": inv.id, "internal_state": "invoiced"})
            _logger.info("UPDATED PAYMENTS...")

        collection_plan = self.env["collection_plan.collection_plan"].browse(
            self.collection_plan_id.id
        )
        _logger.info("COLLECTION_PLAN: %s" % collection_plan)
        collection_plan.write({"invoice_ids": [(4, inv.id)]})
        _logger.info("UPDATED COLLECTION_PLAN...")

        collection_plan.update_payed()
        collection_plan.change_state_collection_plan()
        return self.open_invoices(inv.id)

    @api.multi
    def create_payments_and_invoice(self):
        inv_obj = self.env["account.invoice"]

        # try:
        inv_lines = []

        for payment in self.payment_term_ids:
            if payment.description:
                name = payment.description
            else:
                name = "Contrato: %s - Fecha de pago: %s" % (
                    payment.plan_id.collection_plan_id.contract_id.barcode,
                    payment.payment_date,
                )

            default_product_id = self.env["product.template"].search(
                [("name", "=", "IMPORT SRI PRODUCT")]
            )
            default_product = self.env["product.product"].search(
                [("product_tmpl_id", "=", default_product_id.id)]
            )

            cm_product_template_util_id = default_product_id.product_template_util_id
            if not cm_product_template_util_id:
                raise _(
                    "Accounts for default product is not set correctly for multi company."
                )

            account = cm_product_template_util_id.account_income
            _logger.info("account_income: %s" % str(account))

            account = (
                self.env["account.account"]
                .sudo()
                .search(
                    [
                        ("company_id", "=", self.operating_unit_id.company_id.id),
                        ("code", "=", account.code),
                    ]
                )
            )
            _logger.info("account_income from company: %s" % str(account))

            line = {
                "name": name,
                "account_id": account.id,
                "price_unit": payment.amount,
                "discount": payment.discount,
                "discount_amount": payment.discount,
                "quantity": float(1.0),
                "product_id": default_product.id,
                "account_analytic_id": False,
                "payment_id": payment.id,
            }

            line.update({"invoice_line_tax_id": [(6, 0, payment.tax_ids.ids)]})

            inv_lines.append((0, 0, line))

        _logger.info("INV_LINES: %s" % inv_lines)

        inv_data = self.build_invoice_data(inv_lines)
        _logger.info("INV_DATA: %s" % inv_data)

        inv = inv_obj.create(inv_data)
        _logger.info("INV: %s" % inv)
        inv.button_reset_taxes()
        inv.signal_workflow("invoice_open")

        self.reconcile_previous_payments(inv, self.taxes_included)
        _logger.info("RECONCILE PAYMENTS...")

        for pt in self.payment_term_ids:
            pt.write({"invoice_id": inv.id, "internal_state": "invoiced"})
        _logger.info("UPDATED PAYMENTS...")

        collection_plan = self.env["collection_plan.collection_plan"].browse(
            self.collection_plan_id.id
        )
        _logger.info("COLLECTION_PLAN: %s" % collection_plan)
        collection_plan.write({"invoice_ids": [(4, inv.id)]})
        _logger.info("UPDATED COLLECTION_PLAN...")

        collection_plan.update_payed()
        collection_plan.change_state_collection_plan()
        return self.open_invoices(inv.id)

    @api.multi
    def create_invoice(self):
        if "payment_id" in self._context:
            return self.create_individual_invoice()
        else:
            return self.create_payments_and_invoice()

    @api.multi
    def reconcile_previous_payments(self, inv, taxes_included):
        self.ensure_one()
        # receivable account of the out_invoice
        inv_account_id = inv.account_id
        move_line_ids = []
        # get invoice account.move
        move_id = inv.move_id
        # get invoice account.move account.move.line which account is invoice receivable account
        for line in move_id.line_id:
            if line.account_id.id == inv_account_id.id:
                move_line_ids.append(line.id)
        lines = []
        for pt in self.payment_term_ids:
            lines.append(pt.account_voucher_id.move_ids[0])
            if len(pt.account_voucher_id.move_ids) > 1:
                lines.append(pt.account_voucher_id.move_ids[1])
        # get payments account.move.line which account is invoice receivable account
        for line in lines:
            if line.account_id.id == inv_account_id.id:
                move_line_ids.append(line.id)
        self.env["account.move.line"].browse(move_line_ids).reconcile_partial()

    @api.multi
    def reconcile_payments(self, inv, taxes_included):
        self.ensure_one()
        for pt in self.payment_term_ids:
            if not pt.account_voucher_id:
                pt.generate_voucher(
                    "done",
                    self.partner_id.id,
                    self.company_id.id,
                    "receipt",
                    inv,
                    taxes_included,
                )
            _logger.info("VOUCHER_ID: %s" % pt.account_voucher_id)
