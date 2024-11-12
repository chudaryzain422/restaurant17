# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
#    Author: Aysha Shalin (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
###############################################################################
from odoo import fields,api, models,tools

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
    year = fields.Char(string="Year",default=_get_year)

class SaleOrder(models.Model):
    _inherit = "sale.order"

    season = fields.Selection([
        ('winter', 'Winter'),
        ('spring', 'Spring'),
        ('summer', 'Summer'),
        ('autumn', 'Autumn'),
    ], string='Season',compute="_compute_get_season",store=True)
    event_details = fields.Many2one("sale.season",string="Event",compute="_compute_get_season",store=True)

    @api.depends("date_order")
    def _compute_get_season(self):
        for i in self:
            date = i.date_order
            r = self.env['sale.season'].sudo().search([("start_date",">=",date),("end_date","<=",date)],order="id desc")
            i.event_details = r
            month = date.month
            if month in [12, 1, 2]:
                season= 'winter'
            elif month in [3, 4, 5]:
                season= 'spring'
            elif month in [6, 7, 8]:
                season= 'summer'
            else:
                season = 'autumn'
            i.season = season

    def get_sales_data(self, start_date, end_date):
        sales = self.env['sale.order'].search([
            ('state', 'in', ['sale', 'done'])  # Only include confirmed and completed orders
        ])
        return sales

class SalesReport(models.Model):
    _name ="sale.seasonal.analysis.report"
    _description = "Sales Seasonal Analysis report "
    _auto = False
    _rec_name = 'date_order'

    year = fields.Char(string="Year")
    month = fields.Char(string="Month")
    date_order = fields.Date(string="Order Date")
    season = fields.Char(string="Season")
    event_details = fields.Many2one("sale.season",string="")
    sales_amount = fields.Float(string="Sales Amount")



    def init(self):
        tools.drop_view_if_exists(self._cr, self._table)
        self._cr.execute("""
    CREATE OR REPLACE VIEW  %s as(
         SELECT
         MIN(so.id) AS id,
    EXTRACT(YEAR FROM so.date_order) AS year,
    TO_CHAR(so.date_order, 'Month') AS month,
    so.date_order,
    CASE
        WHEN EXTRACT(MONTH FROM so.date_order) IN (12, 1, 2) THEN 'Winter'
        WHEN EXTRACT(MONTH FROM so.date_order) IN (3, 4, 5) THEN 'Spring'
        WHEN EXTRACT(MONTH FROM so.date_order) IN (6, 7, 8) THEN 'Summer'
        WHEN EXTRACT(MONTH FROM so.date_order) IN (9, 10, 11) THEN 'Autumn'
    END AS season,
    so.event_details,   
    
    SUM(so.amount_total) AS sales_amount
FROM sale_order so
WHERE so.state IN ('sale', 'done')
GROUP BY year, month, season, event_details,so.date_order        )""" % (self._table,))













class SalesYearlyReport(models.Model):
    _name = 'sales.yearly.report'
    _description = 'Sales Yearly Report'

    year = fields.Integer(string='Year', required=True)
    total_sales = fields.Float(string='Total Sales', required=True)
    previous_year_sales_value = fields.Float(string='Previous Year Sales')
    previous_year_sales = fields.Float(string='Previous Year Sales')
    growth_rate = fields.Float(string='Growth Rate (%)')
    company_id = fields.Many2one("res.company", string="CompanyId")

    @api.model
    def get_details(self):
        rec = self.env['sales.yearly.report'].sudo().search([],order="year ASC")
        year =[]
        sales_arr =[]
        pre_sale_arr =[]
        growth =[]
        value=[]
        cagr_value =0.00
        cagr_per =0
        len_arr = len(rec)
        last_entry =0
        first_entry =0
        cagr_period =""
        n_yr=0
        cagrdd =0
        if rec:
            last_entry = rec[len_arr-1]['total_sales']
            first_entry = rec[0]['total_sales']
            cagr_period = ('('+str(rec[0]['year'])+'-'+str(rec[len_arr-1]['year'])+')')
            n_yr =   rec[len_arr-1]['year']-rec[0]['year']
            print("n_yr")
            print(n_yr)
            print("first_entry")
            print(first_entry)
            print("last_entry")
            print(last_entry)
        if n_yr != 0 and first_entry != 0:
            cagr_value = ((last_entry / first_entry) ** (1 / n_yr)) - 1
        else:
            cagr_value = 0
        from odoo.tools.float_utils import float_round
        cagr_per = float_round(cagr_value * 100, precision_digits=2)



        for i in rec:
            year.append(i.year)
            sales_arr.append(i.total_sales)
            pre_sale_arr.append(i.previous_year_sales_value)
            growth.append(i.growth_rate)

        value.append({
            'year': year,
            'total_sales':sales_arr,
            'previous_year_sales': pre_sale_arr,
            'growth_rate': growth,
            'cagr_value':cagr_value,
            'cagr_per':cagr_per,
            'cagr_period':str(cagr_period),
        })
        return value

class StockMove(models.Model):
    """ Extends 'stock.move' and provides methods for retrieving data for
    dashboard."""
    _inherit = "stock.move"

    @api.model
    def get_the_top_products(self):
        """ Returns top ten products and done quantity."""
        company_id = self.env.company.id
        query = '''select product_template.name,sum(product_uom_qty)  from stock_move
            inner join stock_picking on stock_move.picking_id = stock_picking.id
            inner join stock_picking_type on stock_picking.picking_type_id = stock_picking_type.id
            inner join product_product on stock_move.product_id = product_product.id
            inner join product_template on product_template.id = product_product.product_tmpl_id 
            where stock_move.state = 'done' and stock_move.company_id=%s and stock_picking_type.code = 'outgoing' and 
            stock_move.create_date between (now() - interval '10 day') and now()
            group by product_template.name ORDER BY sum DESC''' % company_id
        self._cr.execute(query)
        top_product = self._cr.dictfetchall()
        total_quantity = []
        product_name = []
        for record in top_product[:10]:
            total_quantity.append(record.get('sum'))
            product_name.append(record.get('name')['en_US'])
        value = {'products': product_name, 'count': total_quantity}
        return value

    @api.model
    def top_products_last_ten(self):
        """ Returns top ten products and done quantity for last 10 days."""
        company_id = self.env.company.id
        query = '''select product_template.name,sum(product_uom_qty)  from stock_move
            inner join stock_picking on stock_move.picking_id = stock_picking.id
            inner join stock_picking_type on stock_picking.picking_type_id = stock_picking_type.id
            inner join product_product on stock_move.product_id = product_product.id
            inner join product_template on product_template.id = product_product.product_tmpl_id 
            where stock_move.state = 'done' and stock_move.company_id=%s and stock_picking_type.code = 'outgoing' and 
            stock_move.create_date between (now() - interval '10 day') and now()
            group by product_template.name ORDER BY sum DESC''' % company_id
        self._cr.execute(query)
        top_product = self._cr.dictfetchall()
        total_quantity = []
        product_name = []
        for record in top_product[:10]:
            total_quantity.append(record.get('sum'))
            product_name.append(record.get('name')['en_US'])
        value = {'products': product_name, 'count': total_quantity}
        return value

    @api.model
    def top_products_last_thirty(self):
        """ Returns top ten products and done quantity for last 30 days."""
        company_id = self.env.company.id
        query = '''select product_template.name,sum(product_uom_qty)  from stock_move
                inner join stock_picking on stock_move.picking_id = stock_picking.id
                inner join stock_picking_type on stock_picking.picking_type_id = stock_picking_type.id
                inner join product_product on stock_move.product_id = product_product.id
                inner join product_template on product_template.id = product_product.product_tmpl_id 
                where stock_move.state = 'done' and stock_move.company_id=%s and stock_picking_type.code = 'outgoing' 
                and stock_move.create_date between (now() - interval '30 day') and now()
                group by product_template.name ORDER BY sum DESC''' % company_id
        self._cr.execute(query)
        top_product = self._cr.dictfetchall()
        total_quantity = []
        product_name = []
        for record in top_product[:10]:
            total_quantity.append(record.get('sum'))
            product_name.append(record.get('name')['en_US'])
        value = {'products': product_name, 'count': total_quantity}
        return value

    @api.model
    def top_products_last_three_months(self):
        """ Returns top ten products and done quantity for last 3 months."""
        company_id = self.env.company.id
        query = '''select product_template.name,sum(product_uom_qty)  from stock_move
                    inner join stock_picking on stock_move.picking_id = stock_picking.id
                    inner join stock_picking_type on stock_picking.picking_type_id = stock_picking_type.id
                    inner join product_product on stock_move.product_id = product_product.id
                    inner join product_template on product_template.id = product_product.product_tmpl_id 
                    where stock_move.state = 'done' and stock_move.company_id=%s and stock_picking_type.code ='outgoing' 
                    and stock_move.create_date between (now() - interval '3 month') and now()
                    group by product_template.name ORDER BY sum DESC''' % company_id
        self._cr.execute(query)
        top_product = self._cr.dictfetchall()
        total_quantity = []
        product_name = []
        for record in top_product[:10]:
            total_quantity.append(record.get('sum'))
            product_name.append(record.get('name')['en_US'])
        value = {'products': product_name, 'count': total_quantity}
        return value

    @api.model
    def top_products_last_year(self):
        """ Returns top ten products and done quantity for last year."""
        company_id = self.env.company.id
        query = '''select product_template.name,sum(product_uom_qty)  from stock_move
                        inner join stock_picking on stock_move.picking_id = stock_picking.id
                        inner join stock_picking_type on stock_picking.picking_type_id = stock_picking_type.id
                        inner join product_product on stock_move.product_id = product_product.id
                        inner join product_template on product_template.id = product_product.product_tmpl_id 
                        where stock_move.state = 'done' and stock_move.company_id=%s and 
                        stock_picking_type.code = 'outgoing' and 
                        stock_move.create_date between (now() - interval '1 year') and now()
                        group by product_template.name ORDER BY sum DESC''' % company_id
        self._cr.execute(query)
        top_product = self._cr.dictfetchall()
        total_quantity = []
        product_name = []
        for record in top_product[:10]:
            total_quantity.append(record.get('sum'))
            product_name.append(record.get('name')['en_US'])
        value = {'products': product_name, 'count': total_quantity}
        return value

    @api.model
    def get_stock_moves(self):
        """ Returns location name and quantity_done of stock moves graph"""
        company_id = self.env.company.id
        query = ('''select stock_location.complete_name, count(stock_move.id) from stock_move 
            inner join stock_location on stock_move.location_id = stock_location.id where stock_move.state = 'done' 
            and stock_move.company_id = %s group by stock_location.complete_name''' % company_id)
        self._cr.execute(query)
        stock_move = self._cr.dictfetchall()
        count = []
        complete_name = []
        for record in stock_move:
            count.append(record.get('count'))
            complete_name.append(record.get('complete_name'))
        value = {'name': complete_name, 'count': count}
        return value

    @api.model
    def stock_move_last_ten_days(self, post):
        """ Returns location name and quantity_done of stock moves graph last
        ten days."""
        company_id = self.env.company.id
        query = ('''select stock_location.name,sum(stock_move_line.quantity) from stock_move_line
                        inner join stock_location on stock_move_line.location_id = stock_location.id
                        where stock_move_line.state = 'done' and stock_move_line.company_id = %s
                        and stock_move_line.create_date between (now() - interval '10 day') and now()
                        group by stock_location.name''' % company_id)
        self._cr.execute(query)
        location_quantity = self._cr.dictfetchall()
        quantity_done = []
        name = []
        for record in location_quantity:
            quantity_done.append(record.get('sum'))
            name.append(record.get('name'))
        value = {'name': name, 'count': quantity_done}
        return value

    @api.model
    def this_month(self, post):
        """ Returns location name and quantity_done of stock moves graph for
        current month."""
        company_id = self.env.company.id
        query = ('''select stock_location.name,sum(stock_move_line.quantity) from stock_move_line
                    inner join stock_location on stock_move_line.location_id = stock_location.id
                    where stock_move_line.state = 'done' and stock_move_line.company_id = %s
                    and stock_move_line.create_date between (now() - interval '1 months') and now()
                    group by stock_location.name''' % company_id)
        self._cr.execute(query)
        location_quantity = self._cr.dictfetchall()
        quantity_done = []
        name = []
        for record in location_quantity:
            quantity_done.append(record.get('sum'))
            name.append(record.get('name'))
        value = {'name': name, 'count': quantity_done}
        return value

    @api.model
    def last_three_month(self, post):
        """ Returns location name and quantity_done of stock moves graph for
        last three months."""
        company_id = self.env.company.id
        query = ('''select stock_location.name,sum(stock_move_line.quantity) from stock_move_line
                        inner join stock_location on stock_move_line.location_id = stock_location.id
                        where stock_move_line.state = 'done' and stock_move_line.company_id = %s
                        and stock_move_line.create_date between (now() - interval '3 months') and now()
                        group by stock_location.name''' % company_id)
        self._cr.execute(query)
        location_quantity = self._cr.dictfetchall()
        quantity_done = []
        name = []
        for record in location_quantity:
            quantity_done.append(record.get('sum'))
            name.append(record.get('name'))
        value = {'name': name, 'count': quantity_done}
        return value

    @api.model
    def last_year(self, post):
        """ Returns location name and quantity_done of stock moves graph for
        last year."""
        company_id = self.env.company.id
        query = ('''select stock_location.name,sum(stock_move_line.quantity) from stock_move_line
                       inner join stock_location on stock_move_line.location_id = stock_location.id
                       where stock_move_line.state = 'done' and stock_move_line.company_id = %s 
                       and stock_move_line.create_date between (now() - interval '12 months') and now()
                        group by stock_location.name''' % company_id)
        self._cr.execute(query)
        location_quantity = self._cr.dictfetchall()
        quantity_done = []
        name = []
        for record in location_quantity:
            quantity_done.append(record.get('sum'))
            name.append(record.get('name'))
        value = {'name': name, 'count': quantity_done}
        return value

    @api.model
    def get_dead_of_stock(self):
        """ Returns product name and dead quantity of dead stock graph."""
        company_id = self.env.company.id
        sett_dead_stock_bool = self.env['ir.config_parameter'].sudo(). \
            get_param("inventory_stock_dashboard_odoo.dead_stock_bol", default="")
        sett_dead_stock_quantity = self.env['ir.config_parameter'].sudo().get_param(
            "inventory_stock_dashboard_odoo.dead_stock",
            default="")
        sett_dead_stock_type = self.env['ir.config_parameter'].sudo().get_param(
            "inventory_stock_dashboard_odoo.dead_stock_type",
            default="")
        if sett_dead_stock_bool == "True":
            if sett_dead_stock_quantity:
                out_stock_value = int(sett_dead_stock_quantity)
                query = '''select product_product.id,stock_quant.quantity from product_product
                inner join stock_quant on product_product.id = stock_quant.product_id
                where stock_quant.company_id = %s and product_product.create_date not between (now() - interval '%s %s')
                and now() and product_product.id NOT IN (select product_id from stock_move
                inner join stock_picking on stock_move.picking_id = stock_picking.id
                inner join stock_picking_type on stock_picking.picking_type_id = stock_picking_type.id
                where stock_move.company_id = %s and stock_picking_type.code = 'outgoing' and 
                stock_move.state = 'done'   and stock_move.create_date between (now() - interval '%s %s') and now()
                group by product_id)''' % \
                        (company_id, out_stock_value, sett_dead_stock_type, company_id, out_stock_value,
                         sett_dead_stock_type)
                self._cr.execute(query)
                result = self._cr.fetchall()
                total_quantity = []
                product_name = []
                for record in result:
                    if record[1] > 0:
                        complete_name = self.env['product.product'].browse(record[0]).display_name
                        product_name.append(complete_name)
                        total_quantity.append(record[1])
                value = {
                    'product_name': product_name,
                    'total_quantity': total_quantity
                }
                return value
