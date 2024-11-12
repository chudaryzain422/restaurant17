from odoo import models, fields, api, _


class ExpectedSalesReport(models.Model):
    _name = 'expected.sale.report'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'Expected Sales Report'

    year = fields.Integer(string='Year', required=True)
    start_date = fields.Date(string='Start Date', required=True)
    end_date = fields.Date(string='End Date', required=True)
    expected_sales_amount = fields.Float(string='Expected Sales Amount', required=True)
    actual_sales_amount = fields.Float(string='Actual Sales Amount', compute='_compute_actual_sales', store=True)
    percentage = fields.Float(string='Percentage %', compute='_compute_percentage', store=True)

    @api.depends('expected_sales_amount', 'actual_sales_amount')
    def _compute_percentage(self):
        for record in self:
            if record.expected_sales_amount:
                record.percentage = (record.actual_sales_amount / record.expected_sales_amount) * 100
            else:
                record.percentage = 0

    @api.depends('start_date', 'end_date')
    def _compute_actual_sales(self):
        for record in self:
            # Fetch the POS orders within the specified date range
            orders = self.env['pos.order'].search([
                ('date_order', '>=', record.start_date),
                ('date_order', '<=', record.end_date)
            ])
            total_sales = sum(order.amount_total for order in orders)
            record.actual_sales_amount = total_sales

    def write(self, vals):
        # Call super to perform the usual write operation
        result = super(ExpectedSalesReport, self).write(vals)

        # No need to call update_actual_sales; actual_sales_amount will be computed automatically
        return result

    @api.model
    def create(self, vals):
        # Call super to create the record
        record = super(ExpectedSalesReport, self).create(vals)

        # actual_sales_amount will be computed based on start_date and end_date
        return record
