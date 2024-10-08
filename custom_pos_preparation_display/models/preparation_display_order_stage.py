from odoo import fields, models


class PosPreparationDisplayOrderStage(models.Model):
    _name = 'custom_pos_preparation_display.order.stage'
    _description = "Stage of orders by preparation display"

    stage_id = fields.Many2one('custom_pos_preparation_display.stage', ondelete='cascade')
    preparation_display_id = fields.Many2one("custom_pos_preparation_display.display", ondelete='cascade')
    order_id = fields.Many2one('custom_pos_preparation_display.order', ondelete='cascade')
    done = fields.Boolean("Is the order done")
