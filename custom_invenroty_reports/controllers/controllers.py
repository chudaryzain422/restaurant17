# -*- coding: utf-8 -*-
# from odoo import http


# class CustomInvenrotyReports(http.Controller):
#     @http.route('/custom_invenroty_reports/custom_invenroty_reports', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/custom_invenroty_reports/custom_invenroty_reports/objects', auth='public')
#     def list(self, **kw):
#         return http.request.render('custom_invenroty_reports.listing', {
#             'root': '/custom_invenroty_reports/custom_invenroty_reports',
#             'objects': http.request.env['custom_invenroty_reports.custom_invenroty_reports'].search([]),
#         })

#     @http.route('/custom_invenroty_reports/custom_invenroty_reports/objects/<model("custom_invenroty_reports.custom_invenroty_reports"):obj>', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('custom_invenroty_reports.object', {
#             'object': obj
#         })

