# -*- coding: utf-8 -*-
{
    'name': 'Sale & Invoice Discount',
    'description': 'Manage Discount on Sale Order and Invoice ',
    'summary': '',
    'category': 'Accounting',
    'version': '1.1',
    'website': 'https://eg.linkedin.com/in/mostafa-mohammed-449a8786',
    'author': 'Mostafa Mohamed',
    'depends': ['base', 'account', 'account_accountant', 'sale'],
    'data': ['invoice_discount/invoice_discount_view.xml',
             'sale_discount/sale_discount_view.xml',
             'reports/invoice_report_edit.xml',
             'reports/saleorder_report_edit.xml', ],
    'installable': True,
    'auto_install': False,
    'application': True,
}
