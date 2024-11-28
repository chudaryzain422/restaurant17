# -*- coding: utf-8 -*-

import logging
from datetime import timedelta
from functools import partial
import json
import psycopg2
import pytz
import re

from odoo import api, fields, models, tools, _
from odoo.tools import float_is_zero
from odoo.exceptions import UserError
from odoo.http import request
from odoo.addons import decimal_precision as dp
from odoo.exceptions import UserError, AccessError, ValidationError

_logger = logging.getLogger(__name__)


class PosGrillMethod(models.Model):
    _name = "pos.grill.method"
    _description = "Point of Sale Grill Methods"
    _order = "id desc"
    
    @api.depends('product_ids')
    def _compute_product(self):
        self.product_id = self.product_ids and self.product_ids.ids[0] or False
    
    name = fields.Char(string='Grill Method', required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    code = fields.Char('Code',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]}, copy=False)
    active = fields.Boolean('Active', default=True)
    is_breakfast = fields.Boolean('Is a Breakfast Method')
    #product_id = fields.Many2one('product.product', string='Service', required=True,
    #                domain=[('type','=','service'), ('sale_ok', '=', True)], 
    #                states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    product_id = fields.Many2one('product.product', string='Service', 
                                 compute='_compute_product', readonly=True)
    product_ids = fields.One2many('product.product', 'pos_grill_method_id', 
                                string='Services', copy=True, 
                                domain=[('type','=','service'), ('sale_ok', '=', True)], 
                                states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    
    
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=True, default=lambda self: self.env.user.company_id)
    date = fields.Date(string='Date', readonly=True, index=True, default=fields.Datetime.now)
    user_id = fields.Many2one(
        comodel_name='res.users', string='Chef',
        default=lambda self: self.env.uid,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]},
    )
    state = fields.Selection(
        [('draft', 'New'), ('cancel', 'Cancelled'), ('done', 'Approved')],
        'Status', readonly=True, copy=False, default='draft')    
    note = fields.Html(string='Notes')
    
    bom_count = fields.Integer('# Bill of Material', compute='_compute_bom_count')
    bom_ids = fields.Many2many('mrp.bom', 'bom_grill_rel', 'pos_grill_method_id', 'mrp_bom_id', 
                string="Bill of Materials", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    pos_grill_note_ids = fields.Many2many('pos.grill.note', 'note_grill_rel', 'pos_grill_method_id', 'note_id', 
                string="Kitchen Notes", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    addon_ids = fields.Many2many('mrp.bom', 'bom_addon_grill_rel', 'pos_grill_method_id', 'bom_addon_id', 
                string="Addons", states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    
    
    # image: all image fields are base64 encoded and PIL-supported
    image = fields.Binary(
        "Image", attachment=True,
        help="This field holds the image used as photo for the grill method, limited to 1024x1024px.")
    image_medium = fields.Binary(
        "Medium-sized photo", attachment=True,
        help="Medium-sized photo of the grill method. It is automatically "
             "resized as a 128x128px image, with aspect ratio preserved. "
             "Use this field in form views or some kanban views.")
    image_small = fields.Binary(
        "Small-sized photo", attachment=True,
        help="Small-sized photo of the grill method. It is automatically "
             "resized as a 64x64px image, with aspect ratio preserved. "
             "Use this field anywhere a small image is required.")
    
    _sql_constraints = [
        ('code_company_uniq', 'unique (code,company_id)', 'The code of the grill method must be unique per company !')
    ]
    
    def _compute_bom_count(self):
        for grill_method in self:
            bom_count = len(grill_method.bom_ids) + len(grill_method.addon_ids)
            grill_method.bom_count = bom_count or 0.0

    
    def unlink(self):
        for grill_method in self:
            if grill_method.state not in ('draft', 'cancel'):
                raise UserError(_('You cannot delete an grill method which is not draft or cancelled. You should create a credit note instead.'))
            #elif grill_method.move_name:
            #    raise UserError(_('You cannot delete an grill method which has a pos order.'))
        return super(PosGrillMethod, self).unlink()
    

    
    def action_draft(self):
        return self.write({'state': 'draft'})
    

    
    def action_approve(self):
        return self.write({'state': 'done'})
    

    
    def action_cancel(self):
        return self.write({'state': 'cancel'})
    

    
    def action_view_boms(self):
        self.ensure_one()
        action = self.env.ref('mrp.mrp_bom_form_action').read()[0]
        bom_ids = self.bom_ids.ids + self.addon_ids.ids
        action['domain'] = [('id', 'in', bom_ids)]
        return action
    



class PosGrillNote(models.Model):
    _name = "pos.grill.note"
    _description = "Point of Sale Grill Notes"
    
    name = fields.Char(string='Note', required=True)
    

    
    