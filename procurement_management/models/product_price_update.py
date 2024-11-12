from odoo import models, fields

class ProductPriceUpdate(models.Model):
    _name = 'product.price.update'
    _description = 'Product Price Update'

    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'product_id'

    product_id = fields.Many2one('product.product',string='Product', tracking=True)
    location = fields.Char(string='Location',tracking=True)
    price = fields.Float(string='Price',tracking=True)
    date_updated = fields.Datetime(string='Date Updated', default=fields.Datetime.now)
    # state = fields.Selection([('draft', 'Draft'), ('confirmed', 'Confirmed')], string='Status', default='draft')
    updated_by = fields.Many2one('res.users', string='Updated By', default=lambda self: self.env.user.id, tracking=True)
    vendor_id = fields.Many2one('res.partner', string='Vendor', domain=[('supplier_rank', '>', 0)], required=True,tracking=True)


