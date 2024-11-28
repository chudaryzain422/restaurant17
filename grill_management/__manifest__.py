# -*- coding: utf-8 -*-
{
    'name': "grill_management",

    'summary': "Manage grill operations",

    'description': """This module extends POS to handle:
        - Regular restaurant operations
        - Grill section with weight-based pricing
        - Token generation for grill takeaway
        - Custom receipts""",

    'author': "Pits Solutions",
    'website': "https://www.pitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','barcodes', 'point_of_sale'],

    # always loaded
    'data': [
        'data/pos_grill_data.xml',
        'data/sequence_data.xml',
        'security/ir.model.access.csv',
        'views/pos_grill_sequence.xml',
        'views/pos_config_form.xml',
        'views/res_config_settings_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'grill_management/static/src/**/*'
        ],
    },
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
