# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models
_logger = logging.getLogger(__name__)


class PosConfig(models.Model):
    _inherit = 'pos.config'

    module_pos_grill = fields.Boolean(default=False)
    no_of_print_kot = fields.Integer('Print KOT', required=True, default=0)
    enable_orderline_addons = fields.Boolean('Enable Orderline Addons', default=False)
    enable_display_company_id = fields.Boolean(string="Display Product based on company on grill section ",help="it should be enable for grill section alone,(to hide the readytoeat item from jubail company))")
    pos_manager_ids = fields.Many2many("res.users",string="POS Managers belongs to Configuration", domain=lambda self: [("groups_id", "=",
                                                  self.env.ref("point_of_sale.group_pos_manager").id)])
    need_manager_approval_ondeleteion = fields.Boolean(string="Allow to delete POS Orderline with Manager approval", help="Using Manager approval delete any order line in POS")

    @api.model
    def pos_manage_validation_on_delete_line(self,config,pwd,email):
        """ """
        is_valid = False
        msg=""
        _logger.info("@@@@@@@@@@Test Manager  Approval@@@@@"+str(config))
        pos_config = self.env['pos.config'].sudo().browse(int(config))
        user_rec = self.env['res.users'].sudo().search([("login","=",email),("pos_security_pin","=",pwd),
                                                        ("id","in",pos_config.pos_manager_ids.ids)])
        if user_rec:
            group_pos_manager = self.env.ref('point_of_sale.group_pos_manager')
            if group_pos_manager in user_rec.groups_id:
                      is_valid=True
            else:
                    msg ="Entered Email user is not POS Manager"
        else:
            msg ="No User found with email and Pwd"
        return is_valid,msg





    @api.onchange('module_pos_grill')
    def _onchange_module_pos_grill(self):
        if self.module_pos_grill:
            #self.iface_start_categ_id = self.env.ref('fbu_pos_grill.grill')
            self.iface_start_categ_id = self.env['pos.category'].search([('name', '=like', 'Grill Menu')], order='name asc', limit=1)
            self.no_of_print_recepits = 1
            self.is_posbox = True
            #Product lock was true before - reason unknown
            # self.iface_productlock = False
            # self.iface_categlock = False
            # self.iface_homelock = True
        else:
            self.iface_start_categ_id = self.env['pos.category'].search([('name', '=like', 'MISC%')], order='name asc', limit=1)
            self.no_of_print_recepits = 2
            self.is_posbox = False
            # self.iface_productlock = False
            # self.iface_categlock = True
            # self.iface_homelock = True

    @api.onchange('is_posbox')
    def _onchange_is_posbox(self):
        if self.is_posbox:
            self.proxy_ip = self.env['ir.config_parameter'].sudo().get_param('fbu_pos_grill.pos_proxy_ip', default='10.10.21.247')
            self.iface_electronic_scale = True
