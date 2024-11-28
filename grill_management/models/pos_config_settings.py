# -*- coding: utf-8 -*-

import threading
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ResConfigSettingsInherit(models.TransientModel):
    _inherit = 'res.config.settings'

    def _default_pos_config(self):
        # Default to the last modified pos.config.
        active_model = self.env.context.get('active_model', '')
        if active_model == 'pos.config':
            return self.env.context.get('active_id')
        return self.env['pos.config'].search([('company_id', '=', self.env.company.id)], order='write_date desc', limit=1)

    pos_config_id = fields.Many2one('pos.config', string="Point of Sale",
                                    default=lambda self: self._default_pos_config())
    module_pos_grill = fields.Boolean(related='pos_config_id.module_pos_grill', readonly=False)
