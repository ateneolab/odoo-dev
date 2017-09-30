# -*- coding: utf-8 -*-
{
    'name': "Muestra el PVP en los pedidos",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "AteneoLab C. Ltda.",
    'website': "www.ateneolab.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale', 'product_publichsed_sale_price', 'sale_order_lot_selection'],  # , 'l10n_ec_withdrawing'

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/sale_order_line_view.xml',
        'templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo.xml',
    ],
}