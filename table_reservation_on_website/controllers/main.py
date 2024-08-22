# -*- coding: utf-8 -*-
###############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#
#    Copyright (C) 2024-TODAY Cybrosys Technologies(<https://www.cybrosys.com>)
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
from odoo import http
from odoo.exceptions import ValidationError
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo import SUPERUSER_ID


class WebsiteSalePayment(WebsiteSale):
    """ For creating new record for table reservation """
    @http.route('/shop/payment/validate', type='http', auth="public",
                website=True, sitemap=False)
    def shop_payment_validate(self, sale_order_id=None, **post):
        """ Payment Validate page """
        if sale_order_id is None:
            order = request.website.sale_get_order()
            if not order and 'sale_last_order_id' in request.session:
                last_order_id = request.session['sale_last_order_id']
                order = request.env['sale.order'].sudo().browse(
                    last_order_id).exists()
        else:
            order = request.env['sale.order'].sudo().browse(sale_order_id)
            assert order.id == request.session.get('sale_last_order_id')
        errors = self._get_shop_payment_errors(order)
        if errors:
            first_error = errors[0]  # only display first error
            error_msg = f"{first_error[0]}\n{first_error[1]}"
            raise ValidationError(error_msg)
        tx_sudo = order.get_portal_last_transaction() if order else order.env['payment.transaction']
        if order:
            reservation = request.env['table.reservation'].sudo().create({
                "customer_id": request.env.user.partner_id.id,
                "booked_tables_ids": order.tables_ids,
                "floor_id": order.floors,
                "date": order.date,
                "starting_at": order.starting_at,
                "ending_at": order.ending_at,
                'booking_amount': order.booking_amount,
                'state': 'reserved',
            })
            order.table_reservation_id = reservation.id
        if not order or (order.amount_total and not tx_sudo):
            return request.redirect('/shop')
        if order and not order.amount_total and not tx_sudo:
            order.with_context(send_email=True).with_user(SUPERUSER_ID).action_confirm()
            return request.redirect(order.get_portal_url())
        request.website.sale_reset()
        if tx_sudo and tx_sudo.state == 'draft':
            return request.redirect('/shop')
        return request.redirect('/shop/confirmation')