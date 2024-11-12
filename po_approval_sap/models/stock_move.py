from odoo import models, fields, api

class StockMove(models.Model):
    _inherit = 'stock.move'

    onhand_qty_source = fields.Float(string='On Hand Qty at Source', compute='_compute_onhand_qty_source')

    @api.depends('product_id', 'location_id')
    def _compute_onhand_qty_source(self):
        for move in self:
            quants = self.env['stock.quant'].search([
                ('product_id', '=', move.product_id.id),
                ('location_id', '=', move.location_id.id)
            ])
            move.onhand_qty_source = sum(quants.mapped('quantity'))

