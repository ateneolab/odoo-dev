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
            'barcode': self.barcode,
        })
        
        
    def barcode(self, type, value, width=600, height=100, humanreadable=0):
        width, height, humanreadable = int(width), int(height), bool(humanreadable)
        
        barcode_obj = createBarcodeDrawing(
            type, value=value, format='png', width=width, height=height,
            humanReadable = humanreadable
        )
        
        return base64.encodestring(barcode_obj.asString('png'))
        
        
class report_verification_parser(osv.AbstractModel):
    
    _name = 'report.education_contract_collection_plan.report_verification_document'
    _inherit = 'report.abstract_report'
    _template = 'education_contract_collection_plan.report_verification_document'
    _wrapped_report_class = verification_report_parser
