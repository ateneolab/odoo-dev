# -*- coding: utf-8 -*-

from openerp import models, api, fields
from openerp.osv import osv


class account_type(models.Model):
    _inherit = 'account.invoice'

    discount_scope = fields.Selection(
        [('total_before_tax', u'Total antes de impuestos'), ('per_line_before_tax', u'Por linea antes de impuestos')],
        default='total_before_tax', string=u'Esquema de impuesto', states={'draft': [('readonly', False)]})
    discount_type = fields.Selection(
        [('percent', u'Porcentaje'), ('amount', u'Monto fijo')], u'Tipo de descuento',
        states={'draft': [('readonly', False)]})

    # @api.multi
    # def button_reset_taxes(self):
    #     account_invoice_tax = self.env['account.invoice.tax']
    #     ctx = dict(self._context)
    #     for invoice in self:
    #         id = invoice.id
    #         self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (id,))
    #         # if not invoice.discount_type == 'amount_line':
    #         #     id = invoice.id
    #         #     self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (id,))
    #         # else:
    #         #     id = int(self._context.get('params').get('id'))
    #         #     invoice = self.browse([id])
    #         #     self._cr.execute("DELETE FROM account_invoice_tax WHERE invoice_id=%s AND manual is False", (id,))
    #         self.invalidate_cache()
    #         partner = invoice.partner_id
    #         if partner.lang:
    #             ctx['lang'] = partner.lang
    #         for taxe in account_invoice_tax.compute(invoice.with_context(ctx)).values():
    #             account_invoice_tax.create(taxe)
    #     # dummy write on self to trigger recomputations
    #     return self.with_context(ctx).write({'invoice_line': []})

    # An invoice's residual amount is the sum of its unreconciled move lines and,
    # for partially reconciled move lines, their residual amount divided by the
    # number of times this reconciliation is used in an invoice (so we split
    # the residual amount between all invoice)
    # @api.one
    # @api.depends('invoice_line.price_subtotal', 'tax_line.amount', 'retention_id')
    # def _compute_amount(self):
    #     disc = 0.0
    #     for line in self.invoice_line:
    #         disc += (line.quantity * line.price_unit) * line.discount / 100
    #     self.amount_discount = disc
    #
    #     self.compute_amount()

    # super(account_type, self)._compute_amount()

    # @api.one
    # def compute_amount(self):
    #     self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line)
    # self.write({
    #     'amount_novat': 0.0,
    #     'amount_vat': 0.0,
    #     'amount_tax': 0.0,
    #     'amount_vat_cero': 0.0,
    #     'amount_noret_ir': 0.0,
    #     'amount_tax_retention': 0.0,
    #     'amount_tax_ret_vatb': 0.0,
    #     'taxed_ret_vatb': 0.0,
    #     'amount_tax_ret_vatsrv': 0.0,
    #     'taxed_ret_vatsrv': 0.0,
    #     'amount_tax_ret_ir': 0.0,
    #     'taxed_ret_ir': 0.0,
    #     'amount_ice': 0.0
    # })

    # for line in self.tax_line:
    #     if line.tax_group == 'vat':
    #         self.amount_vat += line.base
    #         self.amount_tax += line.amount
    #     elif line.tax_group == 'vat0':
    #         self.amount_vat_cero += line.base
    #     elif line.tax_group == 'novat':
    #         self.amount_novat += line.base
    #     elif line.tax_group == 'no_ret_ir':
    #         self.amount_noret_ir += line.base
    #     elif line.tax_group in ['ret_vat_b', 'ret_vat_srv', 'ret_ir']:  # estas son las retenciones
    #         self.amount_tax_retention += line.amount
    #         if line.tax_group == 'ret_vat_b':  # in ['ret_vat_b', 'ret_vat_srv']:
    #             self.amount_tax_ret_vatb += line.base
    #             self.taxed_ret_vatb += line.amount
    #         elif line.tax_group == 'ret_vat_srv':
    #             self.amount_tax_ret_vatsrv += line.base
    #             self.taxed_ret_vatsrv += line.amount
    #         elif line.tax_group == 'ret_ir':
    #             self.amount_tax_ret_ir += line.base
    #             self.taxed_ret_ir += line.amount
    #     elif line.tax_group == 'ice':
    #         self.amount_ice += line.amount
    #
    # # if self.amount_vat == 0 and self.amount_vat_cero == 0:
    # #     self.amount_vat_cero = self.amount_untaxed
    #
    # self.amount_total = self.amount_untaxed + self.amount_tax + self.amount_tax_retention
    # self.amount_pay = self.amount_tax + self.amount_untaxed

    # @api.multi
    # def compute_discount(self, discount):  # todo: after taxes
    #     for inv in self:
    #         val1 = val2 = 0.0
    #         disc_amnt = 0.0
    #         val2 = sum(line.amount for line in inv.tax_line)
    #         for line in inv.invoice_line:
    #             val1 += (line.quantity * line.price_unit)
    #             line.discount = discount
    #             line_disc_amnt = (line.quantity * line.price_unit) * discount / 100
    #             disc_amnt += line_disc_amnt
    #             line.discount_amount = line_disc_amnt
    #         total = val1 + val2 - disc_amnt
    #         inv.amount_discount = disc_amnt

    @api.multi
    def compute_discount_amount_per_line(self):  # todo: after taxes
        for inv in self:
            # val1 = val2 = 0.0
            disc_amnt = 0.0
            # val2 = sum(line.amount for line in inv.tax_line)
            for line in inv.invoice_line:
                if inv.discount_type == 'percent':
                    line_disc_amnt = (line.quantity * line.price_unit) * line.discount / 100
                    disc_amnt += line_disc_amnt
                    line.discount_amount = line_disc_amnt
                else:
                    price_subtotal = line.price_unit * line.quantity
                    price_final = price_subtotal - line.discount_amount
                    line_disc_amnt = line.discount_amount if price_final > 0.0 else price_subtotal
                    disc_amnt += line_disc_amnt
                    line.discount_amount = line_disc_amnt
                    line.discount = 0.0
                # disc_amnt = line.discount_amount
                # val1 += disc_amnt

            #     val1 += (line.quantity * line.price_unit)
            #     line.discount = discount
            #     line_disc_amnt = (line.quantity * line.price_unit) * discount / 100
            #     disc_amnt += line_disc_amnt
            #     line.discount_amount = line_disc_amnt
            # total = val1 + val2 - disc_amnt
            inv.amount_discount = disc_amnt

    @api.one
    @api.onchange('discount_type', 'discount_rate', 'discount_scope')
    def supply_rate(self):
        # for inv in self:
        # if self.discount_rate != 0:
        # self.button_reset_taxes()
        amount = sum(line.price_subtotal for line in self.invoice_line)
        tax = sum(line.amount for line in self.tax_line)
        if self.discount_scope == 'total_before_tax':
            if self.discount_type == 'percent':
                self.compute_discount(self.discount_rate)
            elif self.discount_type == 'amount':
                total = 0.0
                discount = 0.0
                for line in self.invoice_line:
                    total += (line.quantity * line.price_unit)
                try:
                    if self.invoice_line:
                        discount = (self.discount_rate / total) * 100
                except:
                    raise osv.except_osv('Error en detalles',
                                         u'Especifique todos los precios y las cantidades de los detalles de la factura.')
                self.compute_discount(discount)
        else:
            self.compute_discount_amount_per_line()

    # _defaults = {
    #     'discount_type': 'amount'
    # }
