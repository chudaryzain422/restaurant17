from odoo import fields, api, models, tools

import time

import datetime
from datetime import datetime, timedelta

from datetime import datetime, date, time


class SaleSeason(models.Model):
    _name = 'sale.season'
    _description = 'Sales Seasons and Holidays'

    def _get_year(self):
        from datetime import date
        today = date.today()
        return today.year

    name = fields.Char(string="Season Name", required=True)
    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    year = fields.Char(string="Year", default=_get_year)

    def generate_line(self):
        """ """
        for ii in self:
            print("UODATE IJDNGD")

            so_query = ("update sale_order set holiday_season_id="+str(ii.id)+" where id in (select id from sale_order where "
                                                                         "date_order>= '"+str(ii.start_date)+"' and date_order<= '"+str(ii.end_date)+"')")
            pos_query = ("update pos_order set holiday_season_id= " + str(
                ii.id) + " where id in (select id from pos_order where "
                         "date_order>= '" + str(ii.start_date) + "' and date_order<= '" + str(ii.end_date) + "')")
            print(so_query)
            print(pos_query)
            self.env.cr.execute(so_query)
            self.env.cr.execute(pos_query)

class POSOrderLine(models.Model):
    _inherit = "pos.order.line"

    product_cost = fields.Float(string='Product Cost')
    total_cost = fields.Float(string='Total Cost')

    @api.depends('product_id')
    def update_cost(self):
        for record in self:
            print("CALINGGGGGGG")
            record.product_cost = record.product_id.standard_price
            record.total_cost = record.product_cost * record.price_unit

    def load_cost(self):
        self.update_cost()




class POSOrder(models.Model):
    _inherit = "pos.order"

    month = fields.Char(string="Month")

    season = fields.Selection([
        ('winter', 'Winter'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
    ], string='Season')

    # event_details = fields.Many2one("sale.season", string="Event", compute="_compute_get_season", store=True)
    holiday_season_id = fields.Many2one('sale.season', string="Sales Season(Holidays)")

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_cost = fields.Float(string='Product Cost', compute="update_cost", store=True)
    total_cost = fields.Float(string='Total Cost', compute="update_cost", store=True)

    @api.depends('product_id')
    def update_cost(self):
        for record in self:
            record.product_cost = record.product_id.standard_price
            record.total_cost = record.product_cost * record.price_unit



class SaleOrder(models.Model):
    _inherit = "sale.order"


    month = fields.Char(string="Month")

    season = fields.Selection([
        ('winter', 'Winter'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
    ], string='Season')

    holiday_season_id = fields.Many2one('sale.season', string="Sales Season(Holidays)")


    @api.model
    def get_details(self):
        domain=[]

        reee =self.env['sale.report'].sudo().search([],limit=1)
        print("RRRRRRRRRRR")
        #
        g_overall_sales_data = self.env['report.all.channels.sales'].read_group(
            domain,['date_order','price_sub_total','product_qty'],['date_order:month','date_order:year']        )
        #
        # g_overall_sales_data = self.env['report.all.channels.sales'].read_group(
        #     domain,
        #     ['month', 'product_id','date_order', 'product_qty', 'cost_price', 'gross_profit', 'price_sub_total'
        #      ],
        #     []
        #
        # )
        print("sdffffffff")
        print(g_overall_sales_data)

        sale_orders = self.env['report.all.channels.sales'].read_group(domain,['date_order','price_sub_total'],['date_order:month','date_order:year'])
        ss_result=[]
        ii=[]
        for data_point in sale_orders:
            month = data_point.get('date_order:month').split(' ')[0]
            if month in ['January','December','February']:
                season = 'winter'
            elif month in ['March', 'April', 'May']:
                season = 'spring'
            elif month in ['June', 'July', 'August']:
                season = 'summer'
            else:
                season = 'autumn'
            ii.append(data_point.get('price_sub_total'))
            ss_result.append({
                           'month':data_point.get('date_order:month'),

                           'total_sales': data_point.get('price_sub_total'),
                           'season': season,

            })
        product_sales = self.env['report.all.channels.sales'].read_group(domain,['date_order','price_sub_total','product_id'],['date_order:month','date_order:year','product_id'])
        # for i  in categories:
        #     top_selling_product_oncategory_keys.append(i.get('sale_category'))
        #     v_domain = [('sale_category','=',i.get('sale_category')),('date_order', '>=', '2023-01-01'), ("date_order", '<=', '2024-01-30'), ('company_id', '=', 1)]
        #
        #     product_categorwise = self.env['report.all.channels.sales'].read_group(
        #         v_domain,
        #         ['product_id','product_qty','date_order','sale_category', 'cost_price', 'gross_profit', 'price_sub_total','team_id','categ_id'],
        #
        #         ['sale_category'], lazy=False,orderby="date_order DESC",limit=10
        #     )
        #
        #     for op in product_categorwise:
        #         data.append({
        #             'gross_profit': op.get('gross_profit'),
        #             'product_id': op.get('product_id'),
        #             'cost_price': op.get('cost_price'),
        #             'product_qty': op.get('product_qty'),
        #             'total_sales': op.get('price_sub_total'),
        #             'year': op.get('date_order:year'),
        #             'categ_id': op.get('categ_id'),
        #             'team_id': op.get('team_id'),
        #             'team_id': i.get('sale_category'),
        #         })

        # g_overall_sales_data = self.env['report.all.channels.sales'].read_group(
        #     domain,
        #     ['month', 'date_order', 'product_qty', 'cost_price', 'gross_profit', 'price_sub_total'
        #      ],
        #     []
        #
        # )
        result=[]
        import pandas as pd

        dd =[]
        Last_month = ""
        total_sales =0
        total_sales_qty =0
        total_cost_price =0
        for data_point in g_overall_sales_data:
            month = data_point.get('date_order:month').split(' ')[0]
            if month in ['January','December','February']:
                season = 'winter'
            elif month in ['March', 'April', 'May']:
                season = 'spring'
            elif month in ['June', 'July', 'August']:
                season = 'summer'
            else:
                season = 'autumn'
            dd.append(data_point.get('price_sub_total'))
            total_sales+=data_point.get('price_sub_total')
            total_sales_qty+=data_point.get('product_qty')
            total_cost_price+=0
            result.append({
                           'month':data_point.get('date_order:month'),
                           # 'holiday_season_id':data_point.get('holiday_season_id'),
                           'year':'2024',
                           # 'sale_category':data_point.get('sale_category'),
                           'gross_profit': data_point.get('gross_profit'),
                           'cost_price': data_point.get('cost_price'),
                           'product_qty': data_point.get('product_qty'),
                           'total_sales': data_point.get('price_sub_total'),
                           # 'team_id': data_point.get('team_id')[1],
                           'season': season,

            })
            Last_month = data_point.get('date_order:month')

        import pandas as pd

        print("DDDDDd")
        print(dd)
        if(len(dd)<=2):
            dd.append(dd[1]+300)



        import pandas as pd
        from statsmodels.tsa.statespace.sarimax import SARIMAX

        # sales_preducton = ', '.join([str(i.total_sales) for i in prediction_result_data])

        # sales_preducton = [for rec in self.filtered(lambda x: x.menu_id)]

        # prediction_result_data.set_index("month", inplace=True)
        # dd.set_index("month", inplace=True)

        sarima_model = SARIMAX(dd, order=(1, 1, 0), seasonal_order=(0, 0, 0, 0))
        sarima_results = sarima_model.fit()

        # Forecasting the next day's sales (Day 8)
        forecast = sarima_results.forecast(steps=3)
        print("SFSDFFSD")
        print(dd)
        prediction_result = []
        print(f"Predicted Sales for Day 8: {forecast}")

        mon_count = 1
        from datetime import datetime
        from dateutil.relativedelta import relativedelta
        input_date = Last_month

        # Convert to datetime object
        date_obj = datetime.strptime(input_date, "%B %Y")

        # Add one month

        for i in list(forecast):
            print(i)
            next_month_date = date_obj + relativedelta(months=mon_count)

            # Output in desired format
            output_date = next_month_date.strftime("%b %Y")
            # forecast_index = pd.date_range(start=data.index[-1] + pd.Timedelta(month=1), periods=3, freq="D")
            prediction_result.append({'month': output_date,
                                      'data': i

                                      })
            mon_count = mon_count + 1
        print("REUSKTLTLT")
        print(result)
        data ={ 'result': result,'prediction_result':prediction_result,
                 'total_sales':total_sales,
            'total_sales_qty':total_sales_qty,
            'total_cost_price':total_cost_price
                }
        print("SDFFFFFFFFFFF")
        print(data)
        return data

        # rec = self.env['sales.order'].sudo().search([], order="year ASC")
        # year = []
        # sales_arr = []
        # pre_sale_arr = []
        # growth = []
        # value = []
        # cagr_value = 0.00
        # cagr_per = 0
        # len_arr = len(rec)
        # last_entry = 0
        # first_entry = 0
        # cagr_period = ""
        # n_yr = 0
        # cagrdd = 0
        # if rec:
        #     last_entry = rec[len_arr - 1]['total_sales']
        #     first_entry = rec[0]['total_sales']
        #     cagr_period = ('(' + str(rec[0]['year']) + '-' + str(rec[len_arr - 1]['year']) + ')')
        #     n_yr = rec[len_arr - 1]['year'] - rec[0]['year']
        #     print("n_yr")
        #     print(n_yr)
        #     print("first_entry")
        #     print(first_entry)
        #     print("last_entry")
        #     print(last_entry)
        # cagr_value = ((last_entry / first_entry) ** (1 / n_yr)) - 1
        # from odoo.tools.float_utils import float_round
        # cagr_per = float_round(cagr_value * 100, precision_digits=2)
        #
        # for i in rec:
        #     year.append(i.year)
        #     sales_arr.append(i.total_sales)
        #     pre_sale_arr.append(i.previous_year_sales_value)
        #     growth.append(i.growth_rate)
        #
        # value.append({
        #     'year': year,
        #     'total_sales': sales_arr,
        #     'previous_year_sales': pre_sale_arr,
        #     'growth_rate': growth,
        #     'cagr_value': cagr_value,
        #     'cagr_per': cagr_per,
        #     'cagr_period': str(cagr_period),
        # })
        # return value

class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    product_cost = fields.Float(string='Product Cost')


class PosOrderLine(models.Model):
    _inherit = "pos.order.line"

    product_cost = fields.Float(string='Product Cost')


class InventoryForecast(models.Model):
    _name = 'inventory.forecast'
    _description = 'Inventory Forecast'

    start_date = fields.Date()
    end_date= fields.Date()
    on_hand_qty = fields.Float()
    company_id = fields.Many2one("res.company")
    product_id = fields.Many2one('product.product', string='Product', required=True)
    quantity_to_purchase = fields.Float(string='Quantity to Purchase', compute='_compute_quantity_to_purchase')
    lead_time = fields.Integer(string='Lead Time (Days)', default=7)
    available_stock = fields.Float(string='Available Stock', compute='_compute_available_stock',store=True)
    expected_stock = fields.Float(string='Purchase Stock', compute='_compute_expected_stock',store=True)
    average_sales = fields.Float(string='Average Sales Qty', compute='_compute_average_sales',store=True)
    growth_rate = fields.Float(string="Growth rate",default=30)
    growth_rate_forecasted_sales = fields.Float(string='Forecasted Qty', compute='_compute_dforecasted_sales',store=True)
    forecasted_sales_next = fields.Float(string='Forecasted Qty (next month Qty)', compute='_compute_forecasted_sales',store=True )
    forecasted_sales_3next = fields.Float(string='Forecasted Qty (next 3 month Qty)', compute='_compute_forecasted_sales',store=True )
    forecast_data = fields.Text(string="")
    expected_sales = fields.Float(string="Expected sales Qty  with Growth",compute='_compute_dforecasted_sales',store=True)

    @api.depends('product_id')
    def _compute_forecasted_sales(self):
        for product in self:
            daily_sales_rate = product.average_sales
            # 3rd month forecast assumes normal sales resume
            growth_factor = 1 + (product.growth_rate / 100)
            forecast_next_month = 30 * daily_sales_rate
            forecast_next_month_w = (30 * daily_sales_rate) * growth_factor
            forecasted_sales_3next = 90 * daily_sales_rate
            forecasted_sales_3next_W = (90 * daily_sales_rate) * growth_factor
            # First 2 months: No fishing allowed, forecast based on past sales
            # forecast_month_1_2 = 60 * daily_sales_rate  # Forecast for first 2 months
            #
            # # Check how much inventory is available
            if product.on_hand_qty >= forecast_next_month:
                forecasted_demand = 0  # Enough inventory for the next 2 months
            else:
                forecasted_demand = forecast_next_month - product.on_hand_qty  # Raise PO to cover shortfall
            product.forecasted_sales_next = forecasted_demand

            if product.on_hand_qty >= forecast_next_month_w:
                forecasted_demand_w = 0  # Enough inventory for the next 2 months
            else:
                forecasted_demand_w = forecast_next_month_w - product.on_hand_qty  # Raise PO to cover shortfall


            if product.on_hand_qty >= forecasted_sales_3next:
                forecasted_demand_9 = 0  # Enough inventory for the next 2 months
            else:
                forecasted_demand_9 = forecasted_sales_3next - product.on_hand_qty  # Raise PO to cover shortfall
            product.forecasted_sales_3next = forecasted_demand_9
            if product.on_hand_qty >= forecasted_sales_3next_W:
                forecasted_demand_9_w = 0  # Enough inventory for the next 2 months
            else:
                forecasted_demand_9_w = forecasted_sales_3next_W - product.on_hand_qty  # Raise PO to cover shortfall



            product.forecast_data = (
                f"Forecasted_demand for next 30days: {forecasted_demand}\n"
                f"Forecasted_demand for next 90days:: {forecasted_demand_9}\n"
                f"Forecasted_demand for next 30days with Growth 30%:: {forecasted_demand_w}\n"
                f"Forecasted_demand for next 90days with Growth 30%:: {forecasted_demand_9_w}\n"
                # f"Average Lead Time (days): {average_lead_time}\n"

            )
            # product.forecasted_sales = forecasted_demand+forecast_month_3  # Add third month's demand

    @api.depends('product_id')
    def _compute_quantity_to_purchase(self):
        for record in self:
            # Logic to compute quantity to purchase based on forecasted sales and available stock
            record.quantity_to_purchase = max(record.forecasted_sales_next - record.available_stock, 0)
            # record.quantity_to_purchase = max(record.forecasted_sales_next - record.available_stock, 0)

    @api.depends('product_id')
    def _compute_available_stock(self):
        for record in self:
            record.available_stock = record.product_id.qty_available
            record.on_hand_qty = record.product_id.qty_available

    @api.depends('product_id')
    def _compute_expected_stock(self):
        for record in self:
            # Example logic for expected stock (can be customized)
            purchase_orders = self.env['purchase.order.line'].search([('product_id', '=', record.product_id.id)])
            record.expected_stock = sum(line.product_qty for line in purchase_orders)

    @api.depends('product_id')
    def _compute_average_sales(self):
        for record in self:
            print("REEE")
            print(record)
            print(record.product_id)
            from dateutil.relativedelta import relativedelta

            # Compute average sales per product from sales orders
            # last_3_month =  fields.Date.today() - relativedelta(months=3)
            sales_orders = self.env['report.all.channels.sales'].read_group([('company_id','=',record.company_id.id),
                                                                         ('date_order', '>=',record.start_date),
                                                                         ('date_order', '<=',record.end_date),
                                                                         ('product_id', '=', record.product_id.id)],
                                                                            fields=['product_qty','product_id'],
                                                                            groupby=['product_id']
                                                                            )
            print("SALES ORDER")
            print(sales_orders)
            total_sales =0
            for line in sales_orders:
                total_sales =line.get('product_qty')
            # total_sales = sum(line.product_qty for line in sales_orders)
            growth_factor = 1 + (record.growth_rate / 100)
            record.expected_sales = total_sales * growth_factor
            record.average_sales = total_sales / 90 # 3 months * 30 days
            # record.category = record.category # 3 months * 30 days
            # record.average_sales = total_sales / days

    @api.depends('product_id')
    def _compute_dforecasted_sales(self):
        for record in self:
            # Logic for forecasted sales, can involve projected growth
            growth_rate = 1.3  # Assume 30% growth
            record.growth_rate_forecasted_sales = record.average_sales * growth_rate

    def get_unique_product_ids(self,company_id,start,end,growth):
        from dateutil.relativedelta import relativedelta
        # last_3_month = fields.Date.today() - relativedelta(months=3)

        # Use ORM to search for all sale order lines and get distinct product_id
        unique_product_ids = self.env['report.all.channels.sales'].read_group(
            domain=[('company_id','=',company_id),('date_order', '>=',start),('date_order', '<=',end)],  # You can add filters here if needed
            fields=['product_id'],
            groupby=['product_id']
        )

        # Extract product IDs from the result
        product_ids = [group['product_id'][0] for group in unique_product_ids if group['product_id']]

        return product_ids

    @api.model
    def train_model(self,company_id,start,end,growth_rate):

        # psql = """ select  l.product_id as product_id  from sale_order_line as l inner join sale_order as s on s.id=l.order_id
        # group by l.product_id
        #        """
        # self.env.cr.execute(psql)
        # sales_data = self.env.cr.fetchall()
        # print(list(sales_data))
        # print("SDFFFFFFFFFFFFFFF")
        # print(list(sales_data)[0])
        product_ids = self.get_unique_product_ids(company_id,start,end,growth_rate)
        for i in product_ids:
            print(i)
            print("DF")
            exisitng_rec = self.search([("product_id","=",i)])
            if exisitng_rec:
                for ii in exisitng_rec:
                    ii.unlink()
            values = {
                    'product_id': int(i),
                'growth_rate':growth_rate,
                'company_id':company_id,
                'start_date':start,
                'end_date':end
                }
            print("DVALUES 000")
            print(values)
            self.create(values)