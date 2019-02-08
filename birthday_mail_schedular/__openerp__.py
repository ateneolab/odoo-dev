# -*- coding: utf-8 -*-
{
    'name': "Birthday Email Scheduler",

    'summary': """
        Send email to the employee when they have their birthday""",

    'description': """
    This module helps the HR to send a birthday reminder to clients who are having birthday on the present day
    
    """,

    'author': "Techspawn Solutions",
    'website': "http://www.techspawn.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'HR',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr'],

    # always loaded
    'data': [

        'schedular.xml',
        'mail_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [

    ],
}
