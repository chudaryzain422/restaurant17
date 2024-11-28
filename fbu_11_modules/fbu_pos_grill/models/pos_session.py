#Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons import decimal_precision as dp


class PosSession(models.Model):
    _inherit = 'pos.session'

    bom_ids = fields.One2many('session.mrp.bom.line', 'session_id', string="Bill of Materials")
    move_raw_ids = fields.One2many('stock.move', 'raw_material_sesssion_id', 'Raw Materials', oldname='move_lines', copy=False)
    stock_moved = fields.Boolean('Stock Moved', copy=False)
    bom_generated = fields.Boolean('BOM Generated', copy=False)
    grill_session = fields.Boolean(related='config_id.module_pos_grill', store=True, copy=False)

    # merge the boms for the session
    def _merge_by_bom(self):
        query = """  """
        args_list = ()
        if len(self.order_ids) > 0:
            args_list += (tuple(self.order_ids.ids),)
            query += """ WHERE pol.order_id IN %s """
            req = """
                SELECT
                    MIN(mb.id) AS id,
                    mb.id AS bom_id,
                    pp.id AS product_id,
                    SUM(pol.qty) AS product_qty
                FROM 
                    mrp_bom mb
                    LEFT JOIN pos_order_line pol on mb.id=pol.bom_id
                    LEFT JOIN product_product pp on pp.product_tmpl_id=mb.product_tmpl_id
                """ + query + """   
                GROUP BY
                    mb.id,
                    pp.id 
                ORDER BY mb.id ASC
            """
            self.env.cr.execute(req, args_list)
            merge_by_bom_data = self.env.cr.dictfetchall()
            return merge_by_bom_data
        return []

    

    # generating bom lines
    def generate_session_marination_lines(self):
        if self.state in ('closed','closing_control','hold_validate'):
            if len(self.bom_ids) > 0:
                self.bom_ids.unlink()
                self.move_raw_ids.filtered(lambda mv: mv.state == 'draft').unlink()
            merge_boms = self._merge_by_bom()
            print('merge_bom', merge_boms)
            for merge_bom in merge_boms:
                self.env['session.mrp.bom.line'].create({
                    'session_id': self.id,
                    'bom_id': merge_bom['bom_id'],
                    'product_id': merge_bom['product_id'],
                    'product_qty': merge_bom['product_qty']
                    })
            self._generate_moves()
        return True


    
    def _generate_moves(self):
        for production in self.bom_ids:
            # production._generate_finished_moves()
            factor = production.product_uom_id._compute_quantity(production.product_qty, production.bom_id.product_uom_id) / production.bom_id.product_qty
            boms, lines = production.bom_id.explode(production.product_id, factor, picking_type=production.bom_id.picking_type_id)
            name = self.name
            procurement_group_id=self.env["procurement.group"].create({'name':name})
            production._generate_raw_moves(lines, procurement_group_id)
            # Check for all draft moves whether they are mto or not
            production.write({'bom_generated': True})
        return True

    
    def confirm_moves(self):
        for production in self:
            # Check for all draft moves whether they are mto or not
            production.move_raw_ids._action_assign()
            production.move_raw_ids.filtered(lambda m: m.state in ['confirmed', 'waiting'])._force_assign()
            production.move_raw_ids.filtered(lambda m: m.product_id.tracking == 'none')._action_done()
            production.write({'stock_moved': True})
        return True

    
    def set_pos_config_vals(self):
        for session in self:
            if session.config_id and session.pos_counter_id:
                vals = {}
                if session.pos_counter_id.grill_counter:
                    iface_start_categ_id = self.env['pos.category'].search([('name', '=like', 'Grill Menu')], order='name asc', limit=1)
                    vals = {
                        'iface_start_categ_id': iface_start_categ_id and iface_start_categ_id.id or False,
                        'no_of_print_recepits': 1,
                        'module_pos_grill': True,
                        'is_posbox': True,
                        'proxy_ip': session.pos_counter_id and session.pos_counter_id.grill_pos_box_ip or '',
                        'iface_productlock': False,
                        'iface_homelock': True,
                        'iface_categlock': False,
                        'iface_scan_via_proxy':False,
                        'iface_electronic_scale': session.pos_counter_id and session.pos_counter_id.iface_electronic_scale or False,
                        'iface_cashdrawer':False,
                        'iface_print_via_proxy':False,
                        'iface_customer_facing_display': session.pos_counter_id and session.pos_counter_id.iface_customer_facing_display or False,
                        'no_of_print_kot': session.pos_counter_id and session.pos_counter_id.no_of_print_kot or 0,
                        'enable_orderline_addons': True,
                        'enable_display_company_id': True, #autoenable the boolean when grill section enable on counter level while open session (check pos_config.py file)
                        # 'printer_ids': [(6, 0, session.pos_counter_id.network_printer_ids.ids)],
                    }
                else:
                    iface_start_categ_id = self.env['pos.category'].search([('name', '=like', 'MISC%')], order='name asc', limit=1)
                    vals = {
                        'iface_start_categ_id': iface_start_categ_id and iface_start_categ_id.id or False,
                        'no_of_print_recepits': 2,
                        'module_pos_grill': False,
                        'is_posbox': False,
                        'proxy_ip': False,
                        #'iface_productlock': False,
                        'iface_productlock': False,
                        'iface_homelock': True,
                        'iface_categlock': True,
                        'iface_scan_via_proxy':False,
                        'iface_electronic_scale':session.pos_counter_id and session.pos_counter_id.iface_electronic_scale or False,
                        'iface_cashdrawer':False,
                        'iface_print_via_proxy':False,
                        'iface_customer_facing_display': session.pos_counter_id and session.pos_counter_id.iface_customer_facing_display or False,
                        'no_of_print_kot': session.pos_counter_id and session.pos_counter_id.no_of_print_kot or 0,
                        'enable_display_company_id': False, #autoenable the boolean when grill section enable on counter level while open session (check pos_config.py file)
                        # 'printer_ids': [(5, 0, session.config_id.printer_ids.ids)],
                    }
                session.config_id.sudo().write(vals)

    
    def action_pos_session_open(self):
        self.set_pos_config_vals()
        return super(PosSession, self).action_pos_session_open()


class SessionBOMLines(models.Model):
    _name = 'session.mrp.bom.line'
    _description = 'Session BOM Lines'

    @api.model
    def _get_default_picking_type(self):
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', 'in', [self.env.context.get('company_id', self.env.user.company_id.id), False])],
            limit=1).id

    @api.model
    def _get_default_location_src_id(self):
        location = False
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id']).default_location_src_id
        if not location:
            location = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
        return location and location.id or False

    @api.model
    def _get_default_location_dest_id(self):
        location = False
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id']).default_location_dest_id
        if not location:
            location = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
        return location and location.id or False

    company_id = fields.Many2one(
        'res.company', 'Company',
        default=lambda self: self.env['res.company']._company_default_get('mrp.production'),
        required=True)
    session_id = fields.Many2one('pos.session', string='Session', readonly=True)
    picking_type_id = fields.Many2one(
        'stock.picking.type', 'Operation Type',
        default=_get_default_picking_type, required=True)
    bom_id = fields.Many2one(
        'mrp.bom', 'Bill of Material',
        readonly=True,
        help="Bill of Materials allow you to define the list of required raw materials to make a finished product.")
    product_id = fields.Many2one(
        'product.product', 'Product',
        domain=[('type', 'in', ['product', 'consu'])],
        readonly=True)
    product_tmpl_id = fields.Many2one('product.template', 'Product Template', related='product_id.product_tmpl_id', readonly=True, store=True)
    product_uom_id = fields.Many2one(
        'uom.uom', 'Product Unit of Measure',
        oldname='product_uom',related='bom_id.product_uom_id', readonly=True,
        store=True)
    product_qty = fields.Float(
        'Quantity Produced', digits=dp.get_precision('Product Unit of Measure'),
        readonly=True)

    #check_to_done = fields.Boolean(compute="_get_produced_qty", string="Check Produced Qty", 
    #    help="Technical Field to see if we can show 'Mark as Done' button")
    #qty_produced = fields.Float(compute="_get_produced_qty", string="Quantity Produced")
    routing_id = fields.Many2one(
        'mrp.routing.workcenter', 'Routing',
        readonly=True, compute='_compute_routing', store=True,
        help="The list of operations (list of work centers) to produce the finished product. The routing "
             "is mainly used to compute work center costs during operations and to plan future loads on "
             "work centers based on production planning.")

    location_src_id = fields.Many2one(
        'stock.location', 'Raw Materials Location',
        default=_get_default_location_src_id,
        readonly=True,  required=True,
        states={'confirmed': [('readonly', False)]},
        help="Location where the system will look for components.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Finished Products Location',
        default=_get_default_location_dest_id,
        readonly=True,  required=True,
        states={'confirmed': [('readonly', False)]},
        help="Location where the system will stock the finished products.")


    
    @api.depends('bom_id', 'bom_id.operation_ids')
    def _compute_routing(self):
        for production in self:
            if production.bom_id.operation_ids:
                production.routing_id = production.bom_id.routing_id.id
            else:
                production.routing_id = False

    @api.onchange('product_id', 'picking_type_id', 'company_id')
    def onchange_product_id(self):
        """ Finds UoM of changed product. """
        if not self.product_id:
            self.bom_id = False
        else:
            bom = self.env['mrp.bom']._bom_find(product=self.product_id, picking_type=self.picking_type_id, company_id=self.company_id.id)
            if bom.type == 'normal':
                self.bom_id = bom.id
            else:
                self.bom_id = False
            self.product_uom_id = self.product_id.uom_id.id
            return {'domain': {'product_uom_id': [('category_id', '=', self.product_id.uom_id.category_id.id)]}}


    def _generate_raw_moves(self, exploded_lines, procurement_group_id):
        self.ensure_one()
        moves = self.env['stock.move']
        for bom_line, line_data in exploded_lines:
            moves += self._generate_raw_move(bom_line, line_data, procurement_group_id)
        return moves
    
    def _generate_raw_move(self, bom_line, line_data, procurement_group_id):
        quantity = line_data['qty']
        # alt_op needed for the case when you explode phantom bom and all the lines will be consumed in the operation given by the parent bom line
        alt_op = line_data['parent_line'] and line_data['parent_line'].operation_id.id or False
        if bom_line.child_bom_id and bom_line.child_bom_id.type == 'phantom':
            return self.env['stock.move']
        if bom_line.product_id.type not in ['product', 'consu']:
            return self.env['stock.move']
        if self.routing_id:
            routing = self.routing_id
        else:
            routing = self.bom_id.routing_id
        if routing and routing.location_id:
            source_location = routing.location_id
        else:
            source_location = self.location_src_id
        # original_quantity = (self.product_qty - self.qty_produced) or 1.0

        customer_loc = self.env.ref('stock.stock_location_customers', raise_if_not_found=False)
        print('customer_loc',customer_loc.id)
        if not customer_loc:
            customer_loc = Location.search([('usage', '=', 'customer')], limit=1)

        data = {
            'sequence': bom_line.sequence,
            'name': procurement_group_id.name,
            'date': self.session_id.start_at,
            'date_expected': self.session_id.start_at,
            'bom_line_id': bom_line.id,
            'product_id': bom_line.product_id.id,
            'product_uom_qty': quantity,
            'product_uom': bom_line.product_uom_id.id,
            'location_id': source_location.id,
            'location_dest_id': customer_loc.id,
            'raw_material_sesssion_id': self.session_id.id,
            'company_id': self.company_id.id,
            'operation_id': bom_line.operation_id.id or alt_op,
            'price_unit': bom_line.product_id.standard_price,
            'procure_method': 'make_to_stock',
            'origin': self.session_id.name,
            'warehouse_id': source_location.get_warehouse().id,
            'group_id': procurement_group_id.id,
            'propagate': True,
            'quantity_done':quantity
            # 'unit_factor': quantity / original_quantity,
        }
        return self.env['stock.move'].create(data)

