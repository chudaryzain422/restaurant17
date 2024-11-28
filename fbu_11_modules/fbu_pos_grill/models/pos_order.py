# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from functools import partial
import json
import psycopg2
import pytz
import re
import pprint

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)

class PosOrder(models.Model):
    _inherit = "pos.order"

    # @api.model
    # def create_from_ui(self, orders):                              
    #     pos_order_ids = super(PosOrder, self).create_from_ui(orders)
    #     if pos_order_ids:
    #         pos_orders = self.browse(pos_order_ids)
    #         for pos_order in pos_orders:
    #             if len(pos_order.lines) > 0:
    #                 dict_grill_order_lines_length = len([orderline.id for orderline in pos_order.lines if orderline.pos_grill_method_id or orderline.pos_grill_qty_id])
    #                 if dict_grill_order_lines_length > 0:
    #                     queue_session = request.env['qms.session'].sudo().search([('state', '=', 'opened')], limit=1)
    #                     if queue_session:
    #                         counter_name = pos_order.session_id.pos_counter_id.name.split('-')
    #                         # token_number = str(counter_name[1]) +'-'+ str(pos_order.barcode[9:12])
    #                         if len(counter_name[1]) >= 2:
    #                             token_number = str(counter_name[1][0])+'-'+(counter_name[1][1])+str(pos_order.barcode[9:12])
    #                             qms_token = request.env['qms.token'].create({'order_id':pos_order.id, 'session_id': queue_session[0].id, 'token_number': token_number, 'order_barcode': pos_order.barcode, 'start_at':fields.Datetime.now()})
    #     return pos_order_ids


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"
    _order = 'order_id, sequence, id'

    sequence = fields.Integer(string='Sequence', default=10)
    pos_grill_method_id = fields.Many2one('pos.grill.method', string='Grill Method')
    bom_id = fields.Many2one('mrp.bom', string='Marinade')
    pos_grill_addon_ids = fields.Many2many('mrp.bom', 'posline_bom_addon_rel', 'line_id', 'bom_addon_id', 
                string="Addons")
    pos_grill_note_ids = fields.Many2many('pos.grill.note', 'posline_note_rel', 'line_id', 'note_id', 
                string="Kitchen Notes")
    grill_note = fields.Text(string='Grill Note')
    product_price = fields.Float(string='Product Price', digits=0)
    pos_grill_qty_id = fields.Many2one('pos.grill.qty', string='Grill Qty')
    grill_nqty = fields.Float(string='Grill N Qty', default=1.0)
    fish_id = fields.Many2one('pos.grill.fish', string='Fish', index=True)
    
    

    # Issue  to be fix in javascript
    '''def _order_line_fields(self, line, session_id=None):
        if line and 'pos_grill_note_ids' in line[2]:
            line[2]['pos_grill_note_ids'] = [(6, 0, line[2]['pos_grill_note_ids'])]
        res = super(PosOrderLine, self)._order_line_fields(line=line, session_id=session_id)
        return res'''
    
    
    
    
    