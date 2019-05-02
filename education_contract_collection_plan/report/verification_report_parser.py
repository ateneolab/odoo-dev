# -*- coding: iso-8859-1 -*-=

from openerp.report import report_sxw
from openerp import api, models
from openerp.osv import osv

import base64
from reportlab.graphics.barcode import createBarcodeDrawing


class verification_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(verification_report_parser, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'get_cash_amount': self._get_cash_amount,
            'get_check_amount': self._get_check_amount,
            'get_credit_card_amount': self._get_credit_card_amount,
            'get_plan_detail': self._get_plan_detail,
            'get_course_name': self._get_course_name,
        })

    def _get_course_name(self, code):
        course_id = self.pool.get('op.course').search(self.cr, self.uid, [('code', '=', code)])[0]
        course_id = self.pool.get('op.course').browse(self.cr, self.uid, [course_id])
        return course_id.name

    def _get_cash_amount(self):
        return 'cash amount'

    def _get_check_amount(self):
        return 'check amount'

    def _get_credit_card_amount(self):
        return 'credit card amount'

    def _get_plan_detail(self):
        return 'plan detail'

    def barcode(self, type, value, width=600, height=100, humanreadable=0):
        width, height, humanreadable = int(width), int(height), bool(humanreadable)

        barcode_obj = createBarcodeDrawing(
            type, value=value, format='png', width=width, height=height,
            humanReadable=humanreadable
        )

        return base64.encodestring(barcode_obj.asString('png'))


class report_verification_parser(osv.AbstractModel):
    _name = 'report.education_contract_collection_plan.report_verification_template'
    _inherit = 'report.abstract_report'
    _template = 'education_contract_collection_plan.report_verification_template'
    _wrapped_report_class = verification_report_parser
