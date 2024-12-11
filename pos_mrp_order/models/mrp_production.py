# -*- coding: utf-8 -*-
##############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>
#    Author: Aysha Shalin (odoo@cybrosys.com)
#
#    you can modify it under the terms of the GNU AFFERO
#    GENERAL PUBLIC LICENSE (AGPL v3), Version 3.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU AFFERO GENERAL PUBLIC LICENSE (AGPL v3) for more details.
#
#    You should have received a copy of the GNU AFFERO GENERAL PUBLIC LICENSE
#    (AGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models


class MrpProduction(models.Model):
    """ Extends MRP Production model for creating manufacturing orders from POS
    orders."""
    _inherit = 'mrp.production'

    def create_mrp_from_pos(self, products):
        """ Function for creating manufacturing orders."""
        product_ids = []
        if products:
            for product in products:
                if self.env['product.product'].browse(
                        int(product['id'])).to_make_mrp:
                    flag = 1
                    if product_ids:
                        for product_id in product_ids:
                            if product_id['id'] == product['id']:
                                product_id['qty'] += product['qty']
                                flag = 0
                    if flag:
                        product_ids.append(product)
            for prod in product_ids:
                if prod['qty'] > 0:
                    bom_count = self.env['mrp.bom'].search([
                        ('product_tmpl_id', '=', prod['product_tmpl_id'])])
                    if bom_count:
                        bom_temp = self.env['mrp.bom'].search([
                            ('product_tmpl_id', '=', prod['product_tmpl_id']),
                            ('product_id', '=', False)])
                        bom_prod = self.env['mrp.bom'].search([
                            ('product_id', '=', prod['id'])])
                        if bom_prod:
                            bom = bom_prod[0]
                        elif bom_temp:
                            bom = bom_temp[0]
                        else:
                            bom = []
                        if bom:
                            #this operation type is used for pos saprete location and its
                            operation_type = self.env['stock.picking.type'].search([('warehouse_id.code', '=','WH'),('code', '=', 'mrp_operation')])
                            vals = {
                                'origin': 'POS-' + prod['pos_reference'],
                                'state': 'confirmed',
                                'product_id': prod['id'],
                                'product_tmpl_id': prod['product_tmpl_id'],
                                'product_uom_id': prod['uom_id'],
                                'product_qty': prod['qty'],
                                'bom_id': bom.id,
                                'picking_type_id': operation_type.id or False,
                            }
                            mrp_order = self.sudo().create(vals)
                            list_value = []
                            for bom_line in mrp_order.bom_id.bom_line_ids:
                                list_value.append((0, 0, {
                                    'raw_material_production_id': mrp_order.id,
                                    'name': mrp_order.name,
                                    'product_id': bom_line.product_id.id,
                                    'product_uom': bom_line.product_uom_id.id,
                                    'product_uom_qty': (bom_line.product_qty * mrp_order.product_qty)/self.env['mrp.bom'].search([("product_tmpl_id", "=", prod['product_tmpl_id'])]).product_qty,
                                    'picking_type_id': mrp_order.picking_type_id.id,
                                    'location_id': mrp_order.location_src_id.id,
                                    # 'location_dest_id': bom_line.product_id.with_company(self.company_id.id).property_stock_production.id,
                                    'company_id': mrp_order.company_id.id,
                                }))
                            finished_vals = {
                                'product_id': prod['id'],
                                'product_uom_qty': prod['qty'],
                                'product_uom': prod['uom_id'],
                                'name': mrp_order.name,
                                'date_deadline': mrp_order.date_deadline,
                                'picking_type_id': mrp_order.picking_type_id.id,
                                'location_id': mrp_order.location_src_id.id,
                                'location_dest_id': mrp_order.location_dest_id.id,
                                'company_id': mrp_order.company_id.id,
                                'production_id': mrp_order.id,
                                'warehouse_id': mrp_order.location_dest_id.warehouse_id.id,
                                'origin': mrp_order.name,
                                'group_id': mrp_order.procurement_group_id.id,
                                'propagate_cancel': mrp_order.propagate_cancel,
                            }
                            mrp_order.update({
                                'move_raw_ids': list_value,
                                'move_finished_ids': [
                                    (0, 0, finished_vals)]
                            })
                            # mrp_order.action_confirm()
                            #
                            # # Mark the raw material moves as done
                            # for move in mrp_order.move_raw_ids:
                            #     move._action_confirm()
                            #     move._action_assign()
                            #     move._set_quantity_done(move.product_uom_qty)
                            #     move._action_done()
                            #
                            # # Mark the finished product move as done
                            # for move in mrp_order.move_finished_ids:
                            #     move._action_confirm()
                            #     move._action_assign()
                            #     move._set_quantity_done(move.product_uom_qty)
                            #     move._action_done()
                            #
                            # # Mark the manufacturing order as done
                            # mrp_order.button_mark_done()
        return True
