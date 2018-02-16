# -*- coding: utf-8 -*-
{
    'name': "Force Sale Company",

    'summary': """
        Set company_id to main company and warehouse_id to default warehouse of the main company.""",

    'description': """
        If you delete default warehouse of the main company, this moduel should break.
    """,

    'author': "Solem Consulting",
    'website': "http://www.solemconsulting.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sale',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'templates.xml',
        'views/sale_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}