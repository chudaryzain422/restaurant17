# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools


class PosSaleReport(models.Model):
    _name = "report.all.channels.sales"
    _auto = False

    name = fields.Char('Order Reference', readonly=True)
    partner_id = fields.Many2one('res.partner', 'Partner', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', readonly=True)
    date_order = fields.Datetime(string='Date Order', readonly=True)
    user_id = fields.Many2one('res.users', 'Salesperson', readonly=True)
    categ_id = fields.Many2one('product.category', 'Product Category', readonly=True)
    company_id = fields.Many2one('res.company', 'Company', readonly=True)
    price_total = fields.Float('Total', readonly=True)
    pricelist_id = fields.Many2one('product.pricelist', 'Pricelist', readonly=True)
    country_id = fields.Many2one('res.country', 'Partner Country', readonly=True)
    price_sub_total = fields.Float(string='Price Subtotal', readonly=True)
    product_qty = fields.Float('Product Quantity', readonly=True)
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account', readonly=True)
    team_id = fields.Many2one('crm.team', 'Sales Channel', readonly=True)

    # total_discount = fields.Float(string='Total Discount (From Feb 2020 Inc .VAT)', readonly=True)
    # price_total_untaxed = fields.Float(string='Total Price(Feb 2020 Exclu VAT', readonly=True)
    # price_sub_total = fields.Float(string='Subtotal w/o discount (From Feb 2020 Inc .VAT)', readonly=True)
    cost_price = fields.Float('Total Cost Price',
                              readonly=True)  # Cost price (technically standard_price) of the product @ the time of sales
    gross_profit = fields.Float(
        string='GP Total')  # ((sale - cost)/sale)*100 --> ((price_total - cost_price)/price_total)*100

    def _so(self):
        so_str = """ 
         SELECT sol.id AS id,
                    so.name AS name,
                    so.partner_id AS partner_id,
                    sol.product_id AS product_id,
                    pro.product_tmpl_id AS product_tmpl_id,
                    so.date_order AS date_order,
                    so.user_id AS user_id,
                    pt.categ_id AS categ_id,
                    so.company_id AS company_id,
					((sol.product_uom_qty * sol.price_unit) * (100 - sol.discount) / 100) AS price_total,
                    --sol.price_total  AS price_total,
                    --sol.price_total AS price_total_untaxed,
                    so.pricelist_id AS pricelist_id,
                    rp.country_id AS country_id,

                    (sol.product_uom_qty * sol.price_unit) AS price_sub_total,
                    (sol.product_uom_qty / u.factor * u2.factor) as product_qty,
                    so.analytic_account_id AS analytic_account_id,
                    so.team_id AS team_id,
                    pt.list_price  AS cost_price,
                    CASE WHEN sol.price_total != 0.00 
                            THEN ((sol.price_subtotal)) * 100
                        ELSE 0
                    END AS gross_profit


            FROM sale_order_line sol
                    JOIN sale_order so ON (sol.order_id = so.id)
                    LEFT JOIN product_product pro ON (sol.product_id = pro.id)
                    JOIN res_partner rp ON (so.partner_id = rp.id)
                    LEFT JOIN product_template pt ON (pro.product_tmpl_id = pt.id)
                    LEFT JOIN product_pricelist pp ON (so.pricelist_id = pp.id)
                    LEFT JOIN uom_uom u on (u.id=sol.product_uom)
                    LEFT JOIN uom_uom u2 on (u2.id=pt.uom_id)
            WHERE so.state != 'cancel'"""

        return so_str

    def _pos(self):
        pos_str = """
                 SELECT
                    pol.id AS id,
                    pos.name AS name,
                    pos.partner_id AS partner_id,
                    pol.product_id AS product_id,
                    pro.product_tmpl_id AS product_tmpl_id,
                    pos.date_order AS date_order,
                    pos.user_id AS user_id,
                    pt.categ_id AS categ_id,
                    pos.company_id AS company_id,
                    ((pol.qty * pol.price_unit) * (100 - pol.discount) / 100) AS price_total,
                    pos.pricelist_id AS pricelist_id,
                    rp.country_id AS country_id,
                    (pol.qty * pol.price_unit) AS price_subtotal,
                    (pol.qty * u.factor) AS product_qty,
                    NULL AS analytic_account_id,
                    NULL AS team_id,
					 pt.list_price  AS cost_price,

                   '0' as gross_profit

                FROM pos_order_line AS pol
                    JOIN pos_order pos ON (pos.id = pol.order_id)
                    LEFT JOIN pos_session session ON (session.id = pos.session_id)
                    LEFT JOIN pos_config config ON (config.id = session.config_id)
                    LEFT JOIN product_product pro ON (pol.product_id = pro.id)
                    LEFT JOIN product_template pt ON (pro.product_tmpl_id = pt.id)
                    LEFT JOIN product_category AS pc ON (pt.categ_id = pc.id)
                    LEFT JOIN res_company AS rc ON (pos.company_id = rc.id)
                    LEFT JOIN res_partner rp ON (rc.partner_id = rp.id)
                    LEFT JOIN uom_uom u ON (u.id=pt.uom_id)
         """
        return pos_str

    def _from(self):
        return """(%s UNION ALL %s)""" % (self._so(), self._pos())

    def get_main_request(self):
        # request = super(PosSaleReport, self).get_main_request()
        request = """
            CREATE or REPLACE VIEW %s AS
                SELECT id AS id,
                    name,
                    partner_id,
                    product_id,
                    product_tmpl_id,
                    date_order,
                    user_id,
                    categ_id,
                    company_id,
                    price_total,
                    pricelist_id,
                    analytic_account_id,
                    country_id,
                    team_id,
                   -- price_subtotal,
                    price_sub_total,
                   --- total_discount,
                    product_qty,
                    cost_price,
                    gross_profit
                    --price_total_untaxed
                FROM %s
                AS foo""" % (self._table, self._from())
        return request

    def init(self):
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute(self.get_main_request())


