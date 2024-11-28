# -*- coding: utf-8 -*-

{
    'name': 'FBU Queue Management',
    'version': '1.0.0',
    'category': 'Point of Sale',
    'sequence': 6,
    'summary': 'Queue Management extensions for the Point of Sale ',
    'description': """

This module adds queue management features to the Point of Sale
""",
    'depends': ['base', 'web', 'point_of_sale', ],
    'website': 'https://www.pitsolutions.com',
    'data': [
        'security/qms_security.xml',
        'security/ir.model.access.csv',
        'views/queue_managment_template.xml',
        'views/qms_view.xml',
        'data/sequence_data.xml',
        'data/queue_management_data.xml',
        # 'views/queue_managment_assets.xml',
        'views/qms_session_view.xml',
        'views/queue_token_view.xml',
        'views/qms_sequence.xml'
    ],
    'assets': {
        'point_of_sale.assets': [
            # 'fbu_queue_management/static/src/js/jquery.scannerdetection.js',
            # 'fbu_queue_management/static/src/js/main.js',
            # 'fbu_queue_management/static/src/less/token_screen.less',
        ],
        # You can add another key if you want to load assets in other parts of Odoo
        'web.assets_backend': [
            # 'web/static/src/js/core/*',
            # 'fbu_queue_management/static/src/js/qms_display.js',
            # 'fbu_queue_management/static/src/xml/queue_managment_template.xml'
            # 'fbu_queue_management/static/src/js/main.js',
            # 'fbu_queue_management/static/src/js/jquery.scannerdetection.js',
        ],
        'web.assets_frontend': [
            # 'fbu_queue_management/static/src/js/qms_loading_script.js',
            # 'fbu_queue_management/static/src/js/qms_display.js',
            'fbu_queue_management/static/src/less/token_screen.less',
        ],
        # 'web.assets_qweb': [
        #     'fbu_queue_management/static/src/xml/*.xml',  # Include any QWeb templates
        # ],

    },
    'qweb': ['static/src/xml/queue.xml'],
    'demo': [],
    'installable': True,
    'auto_install': False,
}
