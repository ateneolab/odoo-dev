# -*- coding: utf-8 -*-
{
    'name': "Educational Contract",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Solem Consulting",
    'website': "http://www.solemconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Education Contract',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'account_voucher', 'sale', 'openeducat_erp', 'mail', 'hr', 'advance_salary',
                'operating_unit', 'oeducat_roll_state', 'scrollable_tree_view', 'oeducat_attendance'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/sale_order_view.xml',
        'views/contract_view.xml',
        'data/change_menu.xml',
        'views/menu.xml',
        'views/student_view.xml',
        'views/workflow.xml',
        'views/company_view.xml',
        'views/conciliation_view.xml',
        'views/op_roll_number_view.xml',
        'views/op_student_view.xml',
        'wizards/report_rpm.xml',
        'report/view_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}
