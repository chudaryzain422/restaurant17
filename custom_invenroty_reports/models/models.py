# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class custom_invenroty_reports(models.Model):
#     _name = 'custom_invenroty_reports.custom_invenroty_reports'
#     _description = 'custom_invenroty_reports.custom_invenroty_reports'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100

