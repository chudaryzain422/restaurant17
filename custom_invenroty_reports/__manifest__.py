# -*- coding: utf-8 -*-
{
    'name': "custom_invenroty_reports",

    'summary': "This module is for custom inventory reports like turnover report and abc analysis report",

    'description': """This module is for custom inventory reports like turnover report and abc analysis report""",

    'author': "Pit Solutions",
    'website': "https://www.pitsolutions.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Inventory',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/expected_sales_form.xml',
        # 'views/views.xml',
        # 'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}

