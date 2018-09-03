# -*- coding: iso-8859-1 -*-=

from openerp.report import report_sxw
from openerp import api, models
from openerp.osv import osv


class custom_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context=None):

        super(custom_report_parser, self).__init__(cr, uid, name, context=context)

        wizard_pool = self.pool.get('education_contract.rpm_wizard')
        wizard_obj = wizard_pool.browse(self.cr, self.uid, self.localcontext.get('active_id'))
        contract_ids = wizard_obj.contract_ids

        advances = self._get_cash_advance(contract_ids)

        self.localcontext.update({
            'cash_advance': advances,
            'get_total_cash': self._get_total_cash,
            'get_total_check': self._get_total_check,
            'get_total_transfer': self._get_total_transfer,
            'get_total_voucher': self._get_total_voucher,
            'get_total_advance': self._get_total_advance,
            'get_vouchers': self._get_vouchers,
            'get_cash_deposits': self._get_cash_deposits,
            'get_transfers': self._get_transfers,
            'get_checks': self._get_checks,
        })

    def _get_cash_deposits(self, docs=None):
        plan_ids = [x.plan_id.id for x in docs]

        domain = [('type', '=', 'cash'), ('cash_sub_type', 'in', ['cash']), ('plan_id', 'in', plan_ids),
                  ('state', 'in', ['done'])]
        payment_term_ids = self.pool.get('education_contract.payment_term').search(self.cr, self.uid, domain)
        payment_term_obj = self.pool.get('education_contract.payment_term').browse(self.cr, self.uid, payment_term_ids)

        cash_deposits = []
        for pt in payment_term_obj:
            cash_deposits.append({
                'date': '',
                'amount': pt.amount,
            })

        return cash_deposits

    def _get_transfers(self, docs=None):
        plan_ids = [x.plan_id.id for x in docs]

        domain = [('cash_sub_type', 'in', ['transfer']), ('plan_id', 'in', plan_ids), ('state', 'in', ['done'])]
        payment_term_ids = self.pool.get('education_contract.payment_term').search(self.cr, self.uid, domain)
        payment_term_obj = self.pool.get('education_contract.payment_term').browse(self.cr, self.uid, payment_term_ids)

        data = []
        for pt in payment_term_obj:
            data.append({
                'date': pt.transfer_id.date,
                'amount': pt.amount,
                'owner': pt.transfer_id.owner,
                'auth_number': pt.transfer_id.auth_number,
                'bank': pt.transfer_id.bank.name
            })

        return data

    def _get_checks(self, docs=None):
        plan_ids = [x.plan_id.id for x in docs]

        domain = [('type', 'in', ['check']), ('plan_id', 'in', plan_ids), ('state', 'in', ['done'])]
        payment_term_ids = self.pool.get('education_contract.payment_term').search(self.cr, self.uid, domain)
        payment_term_obj = self.pool.get('education_contract.payment_term').browse(self.cr, self.uid, payment_term_ids)

        data = []
        for pt in payment_term_obj:
            data.append({
                'date': pt.check_id.date,
                'amount': pt.amount,
                'check_number': pt.check_id.check_number,
                'bank': pt.check_id.bank.name,
                'beneficiary': pt.check_id.beneficiary
            })

        return data

    def _get_vouchers(self, docs=None):

        plan_ids = [x.plan_id.id for x in docs]

        domain = ['|', ('type', 'in', ['credit_card']), ('cash_sub_type', 'in', ['debit_card']),
                  ('plan_id', 'in', plan_ids), ('state', 'in', ['done'])]
        payment_term_ids = self.pool.get('education_contract.payment_term').search(self.cr, self.uid, domain)
        payment_term_obj = self.pool.get('education_contract.payment_term').browse(self.cr, self.uid, payment_term_ids)

        vouchers = []
        for pt in payment_term_obj:
            voucher = pt.voucher_id
            vouchers.append({
                'date': voucher.date,
                'card_name': voucher.card_name,
                'voucher_number': voucher.voucher_number,
                'card_number': 'Nombre de tarjeta',
                'auth_number': voucher.auth_number,
                'amount': pt.amount,
            })

        return vouchers

    def _get_cash_advance(self, contract_list=None):

        """wizard_pool = self.pool.get('education_contract.rpm_wizard')
        wizard_obj = wizard_pool.browse(self.cr, self.uid, self.localcontext.get('active_id'))
        
        date_start = wizard_obj.date_start
        date_end = wizard_obj.date_end
        
        domain = [('date', '>=', date_start), ('date', '<=', date_end), ('is_seller_advance', '=', True)]
        
        if wizard_obj.user_id:
            domain.append(('user_id', 'in', wizard_obj.user_id.ids))
        
        salary_advance_ids = self.pool.get('salary.advance').search(self.cr, self.uid, domain)
        salary_advance_obj = self.pool.get('salary.advance').browse(self.cr, self.uid, salary_advance_ids)
        
        advances = []
        for sa in salary_advance_obj:
            advances.append({
                'date': sa.date,
                'user_id': sa.user_id.display_name,
                'concept': sa.reason,
                'amount': sa.advance
            })"""

        docs = contract_list
        plan_ids = [x.plan_id.id for x in docs]

        domain = [('cash_sub_type', 'in', ['cash']), ('plan_id', 'in', plan_ids),
                  ('state', 'in', ['processed', 'to_advance'])]
        payment_term_ids = self.pool.get('education_contract.payment_term').search(self.cr, self.uid, domain)
        payment_term_obj = self.pool.get('education_contract.payment_term').browse(self.cr, self.uid, payment_term_ids)

        advances = []
        for pt in payment_term_obj:
            advances.append({
                'date': pt.salary_advance_id.date,
                'user_id': pt.salary_advance_id.seller_id.display_name,
                'concept': pt.salary_advance_id.salary_advance_id.reason,
                'amount': pt.amount
            })

        return advances

    def _get_total_cash(self, docs=None):
        plan_ids = [x.plan_id.id for x in docs]

        domain = [('type', 'in', ['cash']), ('cash_sub_type', 'in', ['cash']), ('plan_id', 'in', plan_ids),
                  ('state', 'in', ['done'])]
        payment_term_ids = self.pool.get('education_contract.payment_term').search(self.cr, self.uid, domain)
        payment_term_obj = self.pool.get('education_contract.payment_term').browse(self.cr, self.uid, payment_term_ids)

        sum = 0.0

        for pt in payment_term_obj:
            sum += pt.amount

        return sum

    def _get_total_check(self, docs=None):
        plan_ids = [x.plan_id.id for x in docs]

        domain = [('type', 'in', ['check']), ('plan_id', 'in', plan_ids), ('state', 'in', ['done'])]
        payment_term_ids = self.pool.get('education_contract.payment_term').search(self.cr, self.uid, domain)
        payment_term_obj = self.pool.get('education_contract.payment_term').browse(self.cr, self.uid, payment_term_ids)

        sum = 0.0

        for pt in payment_term_obj:
            sum += pt.amount

        return sum

    def _get_total_transfer(self, docs=None):
        plan_ids = [x.plan_id.id for x in docs]

        domain = [('cash_sub_type', 'in', ['transfer']), ('plan_id', 'in', plan_ids), ('state', 'in', ['done'])]
        payment_term_ids = self.pool.get('education_contract.payment_term').search(self.cr, self.uid, domain)
        payment_term_obj = self.pool.get('education_contract.payment_term').browse(self.cr, self.uid, payment_term_ids)

        sum = 0.0

        for pt in payment_term_obj:
            sum += pt.amount

        return sum

    def _get_total_voucher(self, docs=None):
        plan_ids = [x.plan_id.id for x in docs]

        domain = ['|', ('cash_sub_type', 'in', ['debit_card']), ('type', 'in', ['credit_card']),
                  ('plan_id', 'in', plan_ids), ('state', 'in', ['done'])]
        payment_term_ids = self.pool.get('education_contract.payment_term').search(self.cr, self.uid, domain)
        payment_term_obj = self.pool.get('education_contract.payment_term').browse(self.cr, self.uid, payment_term_ids)

        sum = 0.0

        for pt in payment_term_obj:
            sum += pt.amount

        return sum

    def _get_total_advance(self, docs=None):
        plan_ids = [x.plan_id.id for x in docs]

        domain = [('type', 'in', ['cash']), ('plan_id', 'in', plan_ids), ('state', 'in', ['to_advance', 'processed'])]
        payment_term_ids = self.pool.get('education_contract.payment_term').search(self.cr, self.uid, domain)
        payment_term_obj = self.pool.get('education_contract.payment_term').browse(self.cr, self.uid, payment_term_ids)

        sum = 0.0

        for pt in payment_term_obj:
            sum += pt.amount

        return sum


class report_rpm_parser(osv.AbstractModel):
    _name = 'report.education_contract.report_rpm'
    _inherit = 'report.abstract_report'
    _template = 'education_contract.report_rpm'
    _wrapped_report_class = custom_report_parser
