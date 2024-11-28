# -*- coding: utf-8 -*-

{
    'name': 'Point of Sale Counter',
    'version': '17.0.1.0',  # Updated to Odoo 17 format
    'category': 'Point Of Sale',
    'sequence': 1,
    'summary': 'Point of Sale Counter',
    'description': "Point of Sale Counter",
    'depends': ['web','point_of_sale'],
    'data': [
        'data/data.xml',
        'security/ir.model.access.csv',
        'views/pos_counter_view.xml',
        # 'views/pos_counter_templates.xml',  # Reference the updated XML file
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_counter/static/src/css/pos.css',
            'pos_counter/static/src/js/pos_counter.js',
        ],
        'web.assets_qweb': [
            'pos_counter/static/src/xml/pos_counter.xml',
        ],
    },
    'images': [],
    'license': 'AGPL-3',
    'installable': True,
    'application': True,
    'auto_install': False,
}
