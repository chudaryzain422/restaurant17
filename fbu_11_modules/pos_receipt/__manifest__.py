# -*- coding: utf-8 -*-
{
    'name': 'Point of Sale Receipt',
    'version': '17.0.1.0',
    'category': 'Point Of Sale',
    'sequence': 1,
    'summary': 'Point of Sale Receipt',
    'description': """
        This module enhances the Point of Sale by adding receipt features,
        including extended cart receipts, multi-currency support, order returns,
        grill features, cutting service, and vouchers.
    """,
    'depends': [
        'point_of_sale',
        # 'fbu_pos_configuration',
        # 'pos_extend_cart_location',
        # 'pos_multi_currency_payment',
        # 'pos_order_return',
        'fbu_pos_grill',
        # 'fbu_pos_cutting_service',
        # 'pos_voucher',
    ],
    'data': [
        # 'views/pos_extend_template.xml',
        'views/pos_config_view.xml',
    ],
    'assets': {
        'point_of_sale._assets_pos': [
            'pos_receipt/static/src/css/pos.css',
            'pos_receipt/static/src/js/pos_receipt.js',
            'pos_receipt/static/src/xml/pos_cart_recepit.xml',
            'pos_receipt/static/src/xml/pos_receipt.xml',
        ],
        'web.assets_qweb': [
            'pos_receipt/static/src/xml/pos_cart_recepit.xml',
            'pos_receipt/static/src/xml/pos_receipt.xml',
        ],
    },
    'installable': True,
    'application': True,
}
