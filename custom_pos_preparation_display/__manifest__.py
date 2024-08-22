# -*- coding: utf-8 -*-
{
    'name': 'Custom PoS Preparation Display',
    'version': '1.0.1',
    'category': 'Sales/Point of Sale',
    'sequence': 7,
    'summary': 'Custom implementation to display Orders for Preparation stage.',
    'author': 'Pit Solutions',
    'company': 'Pit Solutions',
    'maintainer': 'Professional IT Solutions',
    'website': 'https://www.pitsolutions.com',
    'depends': ['point_of_sale'],
    'data': [
        'security/ir.model.access.csv',
        'security/preparation_display_security.xml',
        'views/preparation_display_assets_index.xml',
        'views/preparation_display_view.xml',
        'wizard/preparation_display_reset_wizard.xml',
        'data/preparation_display_cron.xml',
    ],
    'installable': True,
    'auto_install': True,
    'assets': {
        'custom_pos_preparation_display.assets': [

            # 'preparation_display' bootstrap customization layer
            'web/static/src/scss/functions.scss',
            'custom_pos_preparation_display/static/src/scss/primary_variables.scss',

            # 'webclient' bootstrap customization layer
            ('include', 'web._assets_helpers'),
            ('include', 'web._assets_backend_helpers'),

            'web/static/src/scss/pre_variables.scss',
            'web/static/lib/bootstrap/scss/_variables.scss',
            'web/static/src/webclient/webclient.scss',

            # Import Bootstrap
            ('include', 'web._assets_bootstrap_backend'),

            # Icons
            'web/static/src/libs/fontawesome/css/font-awesome.css',
            'web/static/lib/odoo_ui_icons/*',
            'web/static/src/webclient/icons.scss',

            ('include', 'web._assets_core'),

            'bus/static/src/services/bus_service.js',
            'bus/static/src/bus_parameters_service.js',
            'bus/static/src/multi_tab_service.js',
            'bus/static/src/workers/*',

            'point_of_sale/static/src/sounds/notification.wav',
            'point_of_sale/static/src/app/sound/sound_service.js',

            'custom_pos_preparation_display/static/src/app/**/*',
        ],
        'point_of_sale._assets_pos': [
            'custom_pos_preparation_display/static/src/override/**/*.js',
        ],
        'point_of_sale.assets_qunit_tests': [
            'custom_pos_preparation_display/static/tests/*.js',
        ],
        'web.assets_tests': [
            'custom_pos_preparation_display/static/tests/tours/**/*',
        ],
    },
}
