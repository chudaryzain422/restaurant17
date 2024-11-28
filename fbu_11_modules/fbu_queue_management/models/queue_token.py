# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import re

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class QMSToken(models.Model):
    _name = 'qms.token'
    _order = 'id desc'

    QUEUE_STATE = [
        ('progress', 'Preparing'),  # method Preparing
        ('ready', 'Ready For Delivery'), # method Ready for Delivery
        ('delivered', 'Delivered'),  # method delivered
    ]

    name = fields.Char(string='Token ID', required=True, readonly=True, default='/')
    token_number = fields.Char(string='Token Number', required=True, readonly=True)
    user_id = fields.Many2one('res.users', string='Responsible', required=True, index=True, readonly=True, states={'progress': [('readonly', False)]}, default=lambda self: self.env.uid)
    start_at = fields.Datetime(string='Opening Date', readonly=True, default=fields.Datetime.now())
    stop_at = fields.Datetime(string='Closing Date', readonly=True, copy=False)
    session_id = fields.Many2one('qms.session', string='Session', required=True, readonly=True, states={'progress': [('readonly', False)]})
    order_id = fields.Many2one('pos.order', string='Order', required=True, index=True, states={'progress': [('readonly', False)]})
    order_barcode = fields.Char(string='Order Barcode', copy=False, compute='_compute_barcode', store=True, readonly=True)
    order_ref = fields.Char(string='Order Ref', related='order_id.pos_reference', store=True, readonly=True)
    state = fields.Selection(QUEUE_STATE, string='Status', required=True, readonly=True, index=True, copy=False, default='progress')

    _sql_constraints = [('uniq_name', 'unique(name)', "The name of this QMS Token must be unique !")]


    @api.depends('order_ref')
    def _compute_barcode(self):
        barcode = ''
        for token in self:
            if token.order_ref:
                pos_reference = token.order_ref and re.sub("\D", "", token.order_ref) or ''
                barcode +=  ''.join(pos_reference and pos_reference.split("-") or [])
            token.order_barcode = barcode

    @api.model
    def create(self, values):
        qms_ticket_name = self.env['ir.sequence'].with_context().next_by_code('queue_ticket.session')
        if values.get('name'):
            pos_cart_name += ' ' + values['name']
        values.update({
            'name': qms_ticket_name
        })
        res = super(QMSToken, self.with_context()).create(values)
        return res

    def button_delivered(self):
        self.write({'state': 'delivered', 'stop_at':fields.Datetime.now()})
        return True

    def button_ready(self):
        self.write({'state': 'ready'})
        return True

    