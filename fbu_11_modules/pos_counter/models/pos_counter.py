# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging
from datetime import timedelta
from functools import partial
import json
import psycopg2
import pytz
import re

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError, AccessError, ValidationError
from odoo.http import request
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)


class PosCounter(models.Model):
    _name = "pos.counter"
    _description = "PoS Counter"
    _order = "sequence"
        
    sequence = fields.Integer(default=10)
    code = fields.Char('Code',required=True)
    name = fields.Char('Name',required=True)
    grill_counter = fields.Boolean('Grill Counter')
    grill_pos_box_ip = fields.Char('PoS Box IP')
    no_of_print_kot = fields.Integer('No of KOT print', required=True, default=0)
    iface_customer_facing_display = fields.Boolean('Customer Display', default=False)
    iface_electronic_scale = fields.Boolean('Electronic Scale', default=False)
    # no_of_print_reciept = fields.Integer('No of Reciept print', required=True, default=0)
    #network_printer_ids = fields.Many2many('kitchen.printer', 'pos_counter_kitchen_printer_rel', 'counter_id', 'printer_id', string='Order Printers')

    _sql_constraints = [
        ('counter_code_uniq', 'unique (code)', 'The Counter code must be unique !')
    ]    


class PosSession(models.Model):
    _inherit = 'pos.session'
    
    @api.depends('pos_counter_id', 'pos_counter_id.code', 'pos_counter_id.name')
    def _compute_counter(self):
        #This function implemented to reduce js work
        for session in self:
            pos_counter_name = ''       
            if session.pos_counter_id:
                code = session.pos_counter_id.code
                name = session.pos_counter_id.name
                comapny_code = session.config_id.company_id.company_short_code
                pos_counter_name = '%s - %s - %s' % (comapny_code, code, name)
            session.pos_counter_name = pos_counter_name


    pos_counter_id = fields.Many2one('pos.counter', string="Counter", copy=False, readonly=False, states={'opening_control': [('readonly', False)]})
    pos_counter_name = fields.Char(string='Counter Name', compute='_compute_counter', copy=False, store=True, readonly=True)
    
    '''@api.constrains('pos_counter_id', 'state')
    def _check_session_counter(self):
        for session in self:
            pos_counter = session.pos_counter_id       
            running_sessions = self.sudo().search_count([
                                        ('id', '!=', session.id),
                                        ('pos_counter_id', '=', pos_counter.id), 
                                        ('state', 'in', ['opened'])
                                    ])            
            if running_sessions:
                raise ValidationError(_('The counter must be unique per opened session!'))'''  
    
    # 
    # def write(self, vals):
    #     res = super(PosSession, self).write(vals)
    #     if self.pos_counter_id.grill_counter and self.config_id:
    #         val = {
    #             'is_posbox': True,
    #             'proxy_ip': self.pos_counter_id.grill_pos_box_ip and self.pos_counter_id.grill_pos_box_ip or False,
    #             'iface_scan_via_proxy':False,
    #             'iface_electronic_scale':True,
    #             'iface_cashdrawer':False,
    #             'iface_print_via_proxy':False,
    #             'iface_customer_facing_display':False,
    #             # 'printer_ids': [(6, 0, self.pos_counter_id.network_printer_ids.ids)],
    #         }
    #         self.config_id.sudo().write(val)
    #     if not self.pos_counter_id.grill_counter and self.config_id:
    #         val = {
    #             'is_posbox': False,
    #             'proxy_ip': False,
    #             'iface_scan_via_proxy':False,
    #             'iface_electronic_scale':False,
    #             'iface_cashdrawer':False,
    #             'iface_print_via_proxy':False,
    #             'iface_customer_facing_display':False,
    #             # 'printer_ids': [(5, 0, self.config_id.printer_ids.ids)],
    #         }
    #         self.config_id.sudo().write(val)
    #     return res
