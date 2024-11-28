# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
import logging

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError


_logger = logging.getLogger(__name__)


class POSConfig(models.Model):
    _inherit = 'pos.config'
    
    no_of_print_recepits = fields.Integer('Print Receipts', required=True, default=2)
    duplicate_receipt_header = fields.Text(string='Duplicate Receipt Header')
    duplicate_receipt_footer = fields.Text(string='Duplicate Receipt Footer')