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


class PosGrillFish(models.Model):
    _name = "pos.grill.fish"
    _description = "POS Grill Fish"
    _order = 'sequence, name'
    
    active = fields.Boolean('Active', default=True)
    sequence = fields.Integer('Sequence', help="Determine the display order")
    name = fields.Char(string='Name', required=True )

    


    

    
    