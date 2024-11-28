# -*- coding: utf-8 -*-

{
    'name': 'Pos Grill Order Sequence',
    'version': '17.0.1.0',  # Updated to Odoo 17 format
    'category': 'Point of Sale',
    'summary': 'Manage Point of Sale Grill Order Sequence',
    'author': 'PIT Solutions',
    'website': "https://www.pitsolutions.ch",
    'company': 'PIT Solutions',
    'depends': ['fbu_pos_grill', 'fbu_queue_management'],
    'data': [
        'security/ir.model.access.csv',
        'data/sequence_data.xml',
        'data/pos_data.xml',
        # 'views/pos_template.xml',
        'views/pos_counter_view.xml',
        'views/pos_grill_sequence.xml',
        'views/pos_order_view.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'fbu_pos_grill_sequence/static/src/js/pos_grill_sequence.js'
        ],
        'web.assets_qweb': [
            'fbu_pos_grill_sequence/static/src/xml/networkprinter_grill_kot.xml',
        ],
    },
    'images': ['static/description/banner.jpg'],
    'license': 'AGPL-3',
    'installable': True,
    'application': False,
    'auto_install': False,
}
