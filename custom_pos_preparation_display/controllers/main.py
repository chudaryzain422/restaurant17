# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request

class CustomPosPreparationDisplayController(http.Controller):
    @http.route(['/custom_pos_preparation_display/web/'], type='http', auth='user', methods=['GET'])
    def display_preparation_web(self, display_id=False):
        preparation_display = request.env['custom_pos_preparation_display.display'].search(
            [('id', '=', int(display_id))]
        )

        if not preparation_display:
            return request.redirect('/web#action=custom_pos_preparation_display.action_preparation_display')

        session_info = request.env['ir.http'].session_info()
        session_info['preparation_display'] = preparation_display.read(["id", "name", "access_token"])[0]

        context = {
            'session_info': session_info,
        }

        response = request.render('custom_pos_preparation_display.index', context)
        return response
