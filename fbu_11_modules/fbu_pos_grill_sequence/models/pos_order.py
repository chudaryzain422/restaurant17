# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from functools import partial

import psycopg2
import pytz

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp

_logger = logging.getLogger(__name__)

class PosSession(models.Model):
    _inherit = 'pos.session'
    
    pos_grill_seq_id = fields.Many2one('pos.grill.seq', string="Grill Sequence", 
                                            copy=False, readonly=True,)
    grill_offline_number = fields.Integer(string='Grill Offline No', copy=False)
    grill_label = fields.Char(string='Grill Label')

    '''
    def action_pos_session_close(self):
        for session in self:
            pos_grill_seq_id = session.pos_grill_seq_id
            running_sessions = self.search([
                                        ('id', '!=', session.id), 
                                        ('grill_session', '=', True),
                                        ('pos_grill_seq_id', '=', pos_grill_seq_id.id), 
                                        ('state', 'in', ['opened'])
                                    ])
            if not running_sessions:
                pos_grill_seq_id.write({'sequence_number_next': pos_grill_seq_id.sequence_number_start})        
        return super(PosSession, self).action_pos_session_close()'''    


    def action_pos_session_closing_control(self):
        res = super(PosSession, self).action_pos_session_closing_control()
        for session in self:
            pos_grill_seq_id = session.pos_grill_seq_id
            running_sessions = self.search([
                                        ('id', '!=', session.id), 
                                        ('pos_grill_seq_id', '=', pos_grill_seq_id.id),
                                        ('state', 'in', ['opened'])
                                    ])
            if not running_sessions:
                session.pos_counter_id.sudo().reset_grill_offline_number() #Can't be accurate always! Assuming that counter will not change
                pos_grill_seq_id.write({'sequence_number_next': pos_grill_seq_id.sequence_number_start})        
        return res
    
    @api.onchange('pos_counter_id')
    def _onchange_pos_counter_id(self):
        pos_counter_id = self.pos_counter_id
        if pos_counter_id:
            self.pos_grill_seq_id = pos_counter_id.pos_grill_seq_id.id
            self.grill_offline_number = pos_counter_id.grill_offline_number
            self.grill_session = pos_counter_id.grill_counter
            self.grill_label = pos_counter_id.grill_label


class PosCounter(models.Model):
    _inherit = "pos.counter"

    pos_grill_seq_id = fields.Many2one('pos.grill.seq', string="Grill Sequence", copy=False)
    grill_offline_start = fields.Integer(string='Grill Offline Start')
    grill_offline_number = fields.Integer(string='Grill Offline No')
    grill_label = fields.Char(string='Grill Label')

    def reset_grill_offline_number(self):
        for counter in self:
            grill_offline_number = counter.grill_offline_start
            counter.write({'grill_offline_number': grill_offline_number})
    


class PosOrder(models.Model):
    _inherit = "pos.order"
            
    grill_sequence_number = fields.Char(string='Grill Sequence No', readonly=True, copy=False)
    pos_counter_id = fields.Many2one('pos.counter', related='session_id.pos_counter_id', string="Counter", readonly=True)
    
    @api.model
    def _order_fields(self, ui_order):
        res = super(PosOrder, self)._order_fields(ui_order)
        grill_session = ui_order.get('grill_session', False)
        if grill_session:
            res.update({
                'grill_sequence_number': ui_order['grill_sequence_number'],
                })
        return res

    @api.model
    def create_from_ui(self, orders):                              
        #_logger.info('create_from_ui create_from_ui create_from_ui %s', orders)
        pos_order_ids = super(PosOrder, self).create_from_ui(orders)
        if pos_order_ids:
            pos_orders = self.browse(pos_order_ids)
            for pos_order in pos_orders:
                if len(pos_order.lines) > 0:
                    dict_grill_order_lines_length = len([orderline.id for orderline in pos_order.lines if orderline.pos_grill_method_id or orderline.pos_grill_qty_id or orderline.product_id.ready_to_eat])
                    if dict_grill_order_lines_length > 0:
                        queue_session = request.env['qms.session'].sudo().search([('state', '=', 'opened'), ('company_id', '=', pos_order.session_id.config_id.company_id.id)], limit=1)
                        if queue_session:
                            token_number = pos_order.grill_sequence_number
                            if token_number:
                                qms_token = request.env['qms.token'].create({'order_id':pos_order.id, 'session_id': queue_session[0].id, 'token_number': token_number, 'order_barcode': pos_order.barcode, 'start_at':fields.Datetime.now()})
        return pos_order_ids
    
    
    
