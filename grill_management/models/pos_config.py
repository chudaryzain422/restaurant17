# coding: utf-8
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class PosConfigInherit(models.Model):
    _inherit = 'pos.config'


    module_pos_grill = fields.Boolean("Is a Grill")

    @api.onchange('module_pos_grill')
    def _onchange_module_pos_grill(self):
        if self.module_pos_grill:
            # self.iface_start_categ_id = self.env.ref('fbu_pos_grill.grill')
            self.iface_start_categ_id = self.env['pos.category'].search([('name', '=like', 'Grill Menu')],
                                                                        order='name asc', limit=1)
            self.is_posbox = True
        else:
            self.iface_start_categ_id = self.env['pos.category'].search([('name', '=like', 'MISC%')], order='name asc', limit=1)
            self.is_posbox = False

    @api.onchange('is_posbox')
    def _onchange_is_posbox(self):
        if self.is_posbox:
            self.proxy_ip = self.env['ir.config_parameter'].sudo().get_param('fbu_pos_grill.pos_proxy_ip',
                                                                             default='10.10.21.247')
            self.iface_electronic_scale = True
