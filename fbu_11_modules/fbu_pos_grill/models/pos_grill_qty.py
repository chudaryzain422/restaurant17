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


class PosGrillQty(models.Model):
    _name = "pos.grill.qty"
    _description = "Point of Sale Grill Qty"
    _order = 'sequence, name'
    
    def _get_default_uom_id(self):
        return self.env["uom.uom"].search([], limit=1, order='id').id
    
    name = fields.Char(string='Name', required=True)
    complete_name = fields.Char('Complete Name', compute='_compute_complete_name', store=True)
    qty = fields.Float('Qty', required=True, digits=dp.get_precision('Product Unit of Measure'), default=1)
    product_tmpl_ids = fields.Many2many('product.template', 'product_grill_qty_rel', 'product_tmpl_id', 'qty_id', string="Products")
    #product_tmpl_ids = fields.Many2many('product.template', 'grill_qty_rel', 'qty_id', 'product_tmpl_id', string="Products")
    #uom_id = fields.Many2one('product.uom', 'Unit of Measure',
    #    default=_get_default_uom_id, required=True) #To do : Solve me later
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)
    sequence = fields.Integer('Sequence', help="Determine the display order")
    price = fields.Float('Unit Price')
    active = fields.Boolean('Active', default=True)

    @api.depends('name', 'product_tmpl_ids')
    def _compute_complete_name(self):
        for posgrill_qty in self:
            if posgrill_qty.product_tmpl_ids:
                posgrill_qty.complete_name = '%s %s' % (posgrill_qty.name, [product_tmpl_id.name for product_tmpl_id in posgrill_qty.product_tmpl_ids])
            else:
                posgrill_qty.complete_name = posgrill_qty.name



class PosGrillPrice(models.Model):
    _name = "pos.grill.price"
    _description = "Point of Sale Grill Price"
    
    name = fields.Char(string='Grill Price', required=True)
    active = fields.Boolean('Active', default=True)
    price_lines = fields.One2many('pos.grill.price.line', 'pos_grill_price_id', string='Price Lines')
    company_id = fields.Many2one('res.company', string='Company', required=True, default=lambda self: self.env.user.company_id)


class PosGrillPriceLine(models.Model):
    _name = "pos.grill.price.line"
    _description = "Point of Sale Grill Price Line"
    _order = 'sequence'
    
    pos_grill_price_id = fields.Many2one('pos.grill.price', string='Price Ref', required=True, ondelete='cascade')    
    from_qty = fields.Float('From Qty')   
    to_qty = fields.Float('To Qty')  
    price = fields.Float('Price')  
    use_product_price = fields.Boolean('Use Product Price', default=False)   
    #uom_id = fields.Many2one('product.uom', 'Unit of Measure',
    #    default=_get_default_uom_id, required=True) #To do : Solve me later     
    sequence = fields.Integer('Sequence', help="Determine the display order")
    active = fields.Boolean('Active', default=True)
    

    
    