# -*- coding: utf-8 -*-


from odoo import models, api


class PosOrder(models.Model):
    _inherit = 'pos.order'

    @api.model
    def _get_line_note(self, line):
        return line.note or ''
