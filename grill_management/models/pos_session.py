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

class PosSessionInherit(models.Model):
    _inherit = 'pos.session'

    pos_grill_seq_id = fields.Many2one('pos.grill.seq', string="Grill Sequence",
                                       copy=False, readonly=True, )
    grill_offline_number = fields.Integer(string='Grill Offline No', copy=False)
    grill_label = fields.Char(string='Grill Label')