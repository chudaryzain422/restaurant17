# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Cybrosys Techno Solutions(<https://www.cybrosys.com>)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
#############################################################################
{
    'name': 'Management REport',
    'version': '17.0.1.0.0',
    'summary': """A module for generate inventory turnover analysis report.""",
    'description': """This will helps you to generate inventory turnover 
    analysis report in pdf, xlsx, tree view and graph view.""",
    'category': "Warehouse",
    'author': 'Cybrosys Techno Solutions',
    'company': 'Cybrosys Techno Solutions',
    'maintainer': 'Cybrosys Techno Solutions',
    'website': "https://www.cybrosys.com",
    'depends': ['base', 'stock', 'sale', 'purchase','point_of_sale','crm'],
    'data': [

        'security/ir.model.access.csv',
        'views/menu_items_view.xml',
        'views/inventory_forecast_view.xml',
'report/report_all_channels_sales_views.xml',
        
        'wizards/forecast_analysis_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'https://fonts.googleapis.com/css2?family=Poppins:wght@400;600&amp;display=swap',
            'management_report/static/src/css/sales_dashboard.css',
            'management_report/static/src/js/sales_dashboard.js',
            'management_report/static/src/xml/inventory_dashboard_template.xml',
            'https://cdn.jsdelivr.net/npm/chart.js',
        ],
    },

    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
