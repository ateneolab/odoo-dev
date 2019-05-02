# -*- coding: iso-8859-1 -*-=

import base64

from reportlab.graphics.barcode import createBarcodeDrawing

from openerp.osv import osv
from openerp.report import report_sxw


class receipt_report_parser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(receipt_report_parser, self).__init__(cr, uid, name, context=context)

        self.localcontext.update({
            'barcode': self.barcode,
        })

    def barcode(self, type, value, width=600, height=100, humanreadable=0):
        width, height, humanreadable = int(width), int(height), bool(humanreadable)

        barcode_obj = createBarcodeDrawing(
            type, value=value, format='png', width=width, height=height,
            humanReadable=humanreadable
        )

        return base64.encodestring(barcode_obj.asString('png'))


class report_rpm_parser(osv.AbstractModel):
    _name = 'report.collection_plan.report_receipt_template'
    _inherit = 'report.abstract_report'
    _template = 'collection_plan.report_receipt_template'
    _wrapped_report_class = receipt_report_parser
