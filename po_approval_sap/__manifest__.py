# -*- coding: utf-8 -*-
{
    'name': "PO Approval from SAP",

    'summary': "this module if for additional approval of Odoo purchase order from SAP",

    'description': """this module if for additional approval of Odoo purchase order from SAP""",

    'author': "PIT Solutions",
    'website': "https://www.pitsolutions.com",

    # for the full list
    'category': 'Integration',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        # 'views/purchase_order_form.xml',
        'views/res_partner_form.xml',
        'views/product_product_form.xml',
        'views/stock_picking_form.xml',
    ],
}

