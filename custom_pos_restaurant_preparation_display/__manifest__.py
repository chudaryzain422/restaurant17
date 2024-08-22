# -*- coding: utf-8 -*-
{
    'name': 'Custom PoS Preparation Display Restaurant',
    'version': '1.0.1',
    'category': 'Sales/Point of Sale',
    'sequence': 7,
    'summary': 'Custom implementation to display Orders for Preparation stage.',
    'author': 'Pit Solutions',
    'company': 'Pit Solutions',
    'maintainer': 'Professional IT Solutions',
    'website': 'https://www.pitsolutions.com',
    'depends': ['pos_restaurant', 'custom_pos_preparation_display'],
    'installable': True,
    'auto_install': True,
    'assets': {
        'custom_pos_preparation_display.assets': [
            'custom_pos_restaurant_preparation_display/static/src/app/**/*',
        ],
        'point_of_sale._assets_pos': [
            'custom_pos_restaurant_preparation_display/static/src/override/**/*.js',
        ],
        'web.assets_tests': [
            'custom_pos_restaurant_preparation_display/static/tests/tours/**/*',
        ],
    },
    'post_init_hook': '_pos_restaurant_preparation_display_post_init',
}
