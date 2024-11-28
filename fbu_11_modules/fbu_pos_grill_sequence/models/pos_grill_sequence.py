# -*- coding: utf-8 -*-

import logging
import string
import re
import random
from odoo import models, fields, api, _
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from datetime import date, datetime

_logger = logging.getLogger(__name__)


class IrSequence(models.Model):
    _inherit = 'ir.sequence'
        
    is_grill = fields.Boolean(string="Is Grill Sequence", default=False)


class PosGrillSequence(models.Model):
    _name = 'pos.grill.seq'
    _description = "POS Grill Sequence"
    _order = 'id desc'


    @api.depends('sequence_id.use_date_range', 'sequence_id.number_next_actual')
    def _compute_seq_number_next(self):
        for grill_seq in self:
            if grill_seq.sequence_id:
                sequence = grill_seq.sequence_id._get_current_sequence()
                grill_seq.sequence_number_next = sequence.number_next_actual
            else:
                grill_seq.sequence_number_next = 100


    def _inverse_seq_number_next(self):
        for grill_seq in self:
            if grill_seq.sequence_id and grill_seq.sequence_number_next:
                sequence = grill_seq.sequence_id._get_current_sequence()
                sequence.sudo().number_next = grill_seq.sequence_number_next


    def _compute_state(self):
        for grill_seq in self:
            state = 'stop'
            running_sessions = self.env['pos.session'].sudo().search([
                                        ('pos_grill_seq_id', '=', grill_seq.id), 
                                        ('state', 'in', ['opened'])
                                    ])
            if running_sessions:
                state = 'run'            
            grill_seq.state = state

    name = fields.Char(string="Name", required=True)
    active = fields.Boolean(string="Active", default=True)
    sequence_id = fields.Many2one('ir.sequence', string='Grill Sequence', required=True, 
                                                    copy=False, domain=[('is_grill', '=', True)])
    sequence_number_start = fields.Integer(string='Start Number', required=True, default=100)
    sequence_number_next = fields.Integer(string='Next Number', compute='_compute_seq_number_next', inverse='_inverse_seq_number_next')
    state = fields.Selection(
        [('run', 'Running'), ('stop', 'Stopped')],
        'Status', readonly=True, compute='_compute_state', store=False, default='stop')
    
    _sql_constraints = [
        ('name_uniq', 'unique (name)', 'Name duplication occured!'),
    ]

    @api.model
    def get_grill_sequence(self, pos_grill_seq_id, **kwargs):
        params = kwargs.get('params', {})
        pos_session_id = params.get('pos_session_id', 0)
        grill_offline_number = params.get('grill_offline_number', 0)
        try:
            pos_grill_seq_id = int(pos_grill_seq_id)
            pos_session_id = int(pos_session_id)
            grill_offline_number = int(grill_offline_number)
        except Exception as e:
            pos_grill_seq_id = 0
            pos_session_id = 0
            grill_offline_number = 0
            
        if grill_offline_number:
            try:
                pos_session = self.env['pos.session'].search([('id', '=', pos_session_id)])
                pos_session.write({'grill_offline_number': grill_offline_number})
                pos_session.pos_counter_id.sudo().write({'grill_offline_number': grill_offline_number})
            except Exception as e:
                _logger.info("Cannot write grill offline number %s" % (e,))           
            
        grill_sequence = []
        grill_seq = self.search([('id', '=', pos_grill_seq_id)])
        if grill_seq:
            sequence_number_next = grill_seq.sequence_id.next_by_id()
            grill_sequence.append({'sequence_number_next': sequence_number_next})
        return grill_sequence


    def reset_grill_sequence(self):
        start_number = 0
        for grill_seq in self:
            grill_seq.sequence_number_next = start_number and start_number or grill_seq.sequence_number_start
        
    
    