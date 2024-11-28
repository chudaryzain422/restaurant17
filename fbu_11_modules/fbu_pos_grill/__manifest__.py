# -*- coding: utf-8 -*-


{
    'name': 'FBU Grill',
    'version': '1.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'Grill extensions for the Point of Sale ',
    'description': """

This module adds several grill features to the Point of Sale:
- Bill Printing: Allows you to print a receipt before the order is paid
- Bill Splitting: Allows you to split an order into different orders
- Kitchen Order Printing: allows you to print orders updates to kitchen or bar printers

""",
    'depends': ['point_of_sale', 'mrp', 'pos_counter'],
    'website': 'https://www.pitsolutions.com',
    'data': [
        'data/pos_grill_data.xml',
        'security/fbu_pos_grill_security.xml',
        'security/ir.model.access.csv',
        # 'views/pos_grill_templates.xml',
        'views/pos_grill_method_views.xml',
        'views/pos_grill_qty_views.xml',
        'views/pos_grill_fish_view.xml',
        'views/pos_order_view.xml',
        'views/product_template_view.xml',
        'views/pos_config_views.xml',
        'views/pos_session_view.xml',
        'views/mrp_bom_view.xml',
        'views/posgrill_receipt_pdf_viewer.xml',
        'wizard/import_product.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'fbu_pos_grill/static/src/**/*',
            'fbu_pos_grill/static/src/css/pos_grill.css',
        ],
    },
    'web.assets_qweb': [
        'fbu_pos_grill/static/src/xml/pos_grill.xml',
        'fbu_pos_grill/static/src/xml/pos_manager_approval.xml',
    ],

    'demo': [
        'data/pos_grill_demo.xml',
    ],
    'installable': True,
    'auto_install': False,
}
