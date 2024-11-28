# -*- coding: utf-8 -*-

from odoo import models, fields, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    '''
    def open_session_cb(self):
        res = super(PosConfig, self).open_session_cb()
        if self.current_session_id and self.current_session_id.grill_session and self.current_session_id.pos_counter_id:
            self.current_session_id.write({'grill_offline_number':  self.current_session_id.pos_counter_id.grill_offline_number})
        return res'''