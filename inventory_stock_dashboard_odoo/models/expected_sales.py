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
            # Fetch actual sales using Odoo ORM instead of SQL
            orders = self.env['pos.order'].search([
                ('date_order', '>=', record.start_date),
                ('date_order', '<=', record.end_date),
                ('state', 'in', ['paid', 'done'])  # Include only paid or completed orders
            ])
            total_sales = sum(order.amount_total for order in orders)
            record.actual_sales_amount = total_sales

    # Function to return data for the dashboard (grouped by month, quarter, or year)
    def get_dashboard_data(self, group_by='month'):
        all_sales_data = []

        for record in self.search([]):
            if group_by == 'month':
                sales_data = record._get_grouped_sales_data('month')
            elif group_by == 'quarter':
                sales_data = record._get_grouped_sales_data('quarter')
            else:
                sales_data = record._get_grouped_sales_data('year')
            all_sales_data.extend(sales_data)

        # Aggregate and calculate growth rate
        aggregated_data = self._aggregate_and_calculate_growth(all_sales_data)

        return {
            'total_sales': sum(sale['actual'] for sale in aggregated_data),
            'growth_percentage': self._calculate_growth(aggregated_data),
            'cagr': self._calculate_cagr(aggregated_data),
            'sales_data': {
                'labels': [sale['period'] for sale in aggregated_data],
                'expected_sales': [sale['expected'] for sale in aggregated_data],
                'actual_sales': [sale['actual'] for sale in aggregated_data],
                'growth_rate': [sale['growth_rate'] for sale in aggregated_data],
            },
        }

    # Group sales data using Odoo ORM instead of raw SQL
    def _get_grouped_sales_data(self, group_by='month'):
        if group_by == 'month':
            group_by_field = 'start_date'
            date_format = "TO_CHAR(start_date, 'YYYY-MM')"  # Group by year and month
        elif group_by == 'quarter':
            group_by_field = 'start_date'
            date_format = "TO_CHAR(start_date, 'YYYY-Q')"  # Group by year and quarter
        elif group_by == 'year':
            group_by_field = 'start_date'
            date_format = "TO_CHAR(start_date, 'YYYY')"  # Group by year
        else:
            raise ValueError(f"Unsupported group_by value: {group_by}")

        query = f"""
            SELECT 
                {date_format} AS period,
                SUM(expected_sales_amount) AS expected,
                SUM(actual_sales_amount) AS actual
            FROM 
                expected_sale_report
            WHERE 
                start_date >= %s AND end_date <= %s
            GROUP BY 
                {date_format}
            ORDER BY 
                {date_format}
        """
        self.env.cr.execute(query, (self.start_date, self.end_date))
        result = self.env.cr.fetchall()

        sales_data = []
        for row in result:
            sales_data.append({
                'period': row[0],  # Grouped by period (month, quarter, year)
                'expected': row[1],  # Expected sales amount
                'actual': row[2],  # Actual sales amount
            })

        return sales_data

    # Aggregate data and calculate growth rates
    def _aggregate_and_calculate_growth(self, sales_data):
        aggregated_data = {}
        for sale in sales_data:
            period = sale['period']
            if period not in aggregated_data:
                aggregated_data[period] = {'period': period, 'expected': 0, 'actual': 0, 'growth_rate': 0}
            aggregated_data[period]['expected'] += sale['expected']
            aggregated_data[period]['actual'] += sale['actual']

        # Calculate growth rates
        return self._calculate_growth_for_period(list(aggregated_data.values()))

    def _calculate_growth_for_period(self, sales_data):
        for index, data in enumerate(sales_data):
            if index == 0:
                data['growth_rate'] = 0
            else:
                previous_actual = sales_data[index - 1]['actual']
                current_actual = data['actual']
                data['growth_rate'] = ((current_actual - previous_actual) / previous_actual) * 100 if previous_actual else 0
        return sales_data

    def _calculate_growth(self, sales_data):
        if sales_data and len(sales_data) > 1:
            start_value = sales_data[0]['actual']
            end_value = sales_data[-1]['actual']
            if start_value > 0:
                return round(((end_value - start_value) / start_value) * 100, 2)
        return 0

    def _calculate_cagr(self, sales_data):
        if sales_data and len(sales_data) > 1:
            start_value = sales_data[0]['actual']
            end_value = sales_data[-1]['actual']
            years = len(sales_data)  # Number of periods
            if start_value > 0:
                return round(((end_value / start_value) ** (1 / years) - 1) * 100, 2)
        return 0
