# -*- coding: utf-8 -*-


from odoo import models


class PosPreparationDisplayResetWizard(models.TransientModel):
    _name = 'custom_pos_preparation_display.reset.wizard'
    _description = 'Reset all current order in a preparation display'

    def reset_all_orders(self):
        preparation_display = self.env['custom_pos_preparation_display.display'].search([('id', '=', self.env.context['preparation_display_id'])])
        preparation_display.reset()
