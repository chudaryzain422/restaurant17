# -*- coding: utf-8 -*-
{
    'name': "procurement_management",

    'summary': "This module is for managing price of products on daily basis",

    'description': """This module is for managing price of products on daily basis""",

    'author': "PIT SOLUTIONS",
    'website': "https://www.pitsolutions.com",

    'category': 'purchase',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'purchase'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/product_price_view.xml',
    ],
    # only loaded in demonstration mode
    # 'demo': [
    #     'demo/demo.xml',
    # ],
}

