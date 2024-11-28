import json
from odoo import http
from odoo.http import request


class WebsitePOS(http.Controller):

    @http.route(['/souq_pos_orderreport/view/<int:order_id>'], type='http', auth='public')
    def view_posgrill_orderreport(self, order_id, **post):
        report = request.env['ir.actions.report'].sudo()._render_qweb_pdf('fbu_pos_grill.report_souq_posorder')
        context = dict(request.env.context)
        pdf, o = report.with_context(context).render_qweb_pdf([order_id], data={})
        pdfhttpheaders = [('Content-Type', 'application/pdf'), ('Content-Length', len(pdf))]
        return request.make_response(pdf, headers=pdfhttpheaders)

    @http.route(['/souqpos/print/<int:order_id>'], type='http', auth='public')
    def print_grillpos_order(self, order_id):
        """ POS Recepit as PDF """
        print(order_id)

        url = "/souq_pos_orderreport/view/" + str(order_id)
        vals = {}
        vals['url'] = url
        return request.render('fbu_pos_grill.souq_pos_report_view_pdf', vals)
