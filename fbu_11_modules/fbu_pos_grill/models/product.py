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

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    grill_service = fields.Boolean('Is a grill service')
        
    consumable_bom = fields.Boolean('Is a consumable bom')
    ready_to_eat = fields.Boolean('Is a Ready To Eat Item')
    breakfast = fields.Boolean('Is a Break Fast Item')

    pos_grill_method_id = fields.Many2one('pos.grill.method', string='Grill Method',                                 
                    #domain=[('state','=', 'done')],
                    )
    grill_min_qty = fields.Float('Grill Min Qty', default=0.0)    
    
    pos_grill_qty_ids = fields.Many2many('pos.grill.qty', 
                            'grill_qty_rel', 'product_tmpl_id', 'qty_id', 
                            string="Grill Qty")
    pos_grill_price_id = fields.Many2one('pos.grill.price', string="Grill Price")
    
    
    @api.constrains('pos_grill_method_id')
    def _check_pos_grill_method(self):
        for product in self:
            domain = [
                ('pos_grill_method_id', '!=', False),
                ('pos_grill_method_id', '=', product.pos_grill_method_id.id),
                ('id', '!=', product.id),
            ]
            nproducts = self.search_count(domain)
            if nproducts:
                raise ValidationError(_('You can not have same grill methods on more than one products!'))
            
    
            
            
    @api.onchange('grill_service', 'consumable_bom')
    def _onchange_grill_consumable(self):
        if self.grill_service:
            self.consumable_bom = False
        if self.consumable_bom:
            self.grill_service = False


class ProductProduct(models.Model):
    _inherit = 'product.product'
    
    #pos_grill_method_id = fields.Many2one('pos.grill.method', string='Grill Method',                                 
    #                domain=[('state','=', 'done')],
    #                )
    

    