# -*- coding: utf-8 -*-
{
    'name': "Collections",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Solem Consulting",
    'website': "www.solemconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Collection',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'education_contract'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/collection_plan_view.xml',
        'views/menu_view.xml',
        'views/pyment_term_views.xml',
        'wizard/wizard_invoice_view.xml',
        'wizard/wizard_sale_receipt_view.xml',
        'report/receipt_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
