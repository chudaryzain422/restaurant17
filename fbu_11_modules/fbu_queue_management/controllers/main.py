# -*- coding: utf-8 -*-
import json
import logging
import pprint
import werkzeug.utils

from odoo import http
from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.http import request

_logger = logging.getLogger(__name__)


class QMSController(http.Controller):

    @http.route('/qms/web/queue_ticket', type='http', auth='user')
    def qms_web(self, debug=True, **k):
        # if user not logged in, log him in
        pos_order = {}
        pos_session = request.env['qms.session'].search([
            ('state', '=', 'opened'),
            ('user_id', '=', request.session.uid)], limit=1)
        # _logger.info('pos_sessions feedback with response data %s', pprint.pformat(pos_session))
        # print ('pos_sessions',pos_session)
        if not pos_session:
            return werkzeug.utils.redirect('/web#action=fbu_queue_management.action_client_qms_menu')
        context = {
            'session_info': json.dumps(request.env['ir.http'].session_info()),
            't_session': pos_session,
            't_company': pos_session.company_id
        }
        if 'name' and 't_session' in k:
            pos_order = request.env['pos.order'].search([
            ('state', 'in', ('paid','done',)),
            ('barcode', '=', k['name']),
            ('cpmpany_id', '=', pos_session.company_id.id)])
            context.update({
            'order': pos_order
            })
        else:
            context.update({
            'message_title': 'Error',
            'message_content': 'Order Not Found'
            })
        return request.render('fbu_queue_management.index', qcontext=context)

    
    @http.route('/qms/order/details', type='json', auth='user')
    def qms_order_details(self, debug=False, **post):
        context = {}
        if all(key in post for key in ('barcode', 'session', 'company')):
            if post['barcode'] and int(post.get('session')) > 0 and int(post.get('company')) > 0:
                barcode = post['barcode'][:12]
                pos_order = request.env['pos.order'].sudo().search([('state', 'in', ('paid','done',)), ('barcode', '=', barcode), ('company_id', '=', int(post.get('company')))], limit=1)
                s_qms_token = request.env['qms.token'].sudo().search(['|', ('order_id', '=', pos_order.id), ('session_id', '=', post['session'])], limit=1)
                if len(s_qms_token) > 0:
                    if s_qms_token[0].state == 'progress':
                        s_qms_token[0].sudo().write({'state': 'ready', 'stop_at': fields.Datetime.now()})
                        context.update({
                            'token_status': 'ready',
                        })
                    elif s_qms_token[0].state == 'ready':
                        s_qms_token[0].sudo().write({'state': 'delivered'})
                        context.update({
                            'token_status': 'delivered',
                        })
                    else:
                        context.update({
                            'token_status': s_qms_token[0].state,
                        })
                    context.update({
                        'order_id': s_qms_token[0].order_id.id,
                        'order_name': s_qms_token[0].order_id.pos_reference,
                        'token_number': s_qms_token[0].order_id.grill_sequence_number,
                        'customer_name': s_qms_token[0].order_id.partner_id.name,
                        'order_barcode': s_qms_token[0].order_id.barcode,
                        })
                else:
                    if pos_order:
                        counter_name = pos_order.session_id.pos_counter_id.name.split('-')
                        token_number = str(counter_name[1])+'-'+(counter_name[1][2])+str(pos_order.barcode[9:12])
                        qms_token = request.env['qms.token'].create({
                            'order_id':pos_order.id, 
                            'session_id': post['session'], 
                            'token_number': pos_order.grill_sequence_number, 
                            'start_at':fields.Datetime.now()
                            })
                        if qms_token:
                            context.update({
                                'qms_token': qms_token[0].name,
                                'token_status': qms_token[0].state,
                                'token_number': s_qms_token[0].order_id.grill_sequence_number,
                            })
        return context

    @http.route('/qms/order/token/create', type='json', auth='user')
    def qms_token_create(self, debug=False, **post):
        context = {}
        s_qms_token = request.env['qms.token'].sudo().search(['|', '|', ('order_id', '=', post['order_id']), ('session_id', '=', post['session_id']), ('token_number', '=', post['token_number'])], limit=1)
        if len(s_qms_token) > 0:
            qms_token = s_qms_token[0]
            qms_token.sudo().write({'state': 'progress'})
        else:
            qms_token = request.env['qms.token'].create({'order_id':post['order_id'], 'session_id': post['session_id'], 'token_number': post['token_number'], 'order_barcode': post['order_barcode'], 'start_at':fields.Datetime.now()})
        if qms_token:
            context.update({
                'qms_token': qms_token[0].name,
                'token_status': qms_token[0].state,
            })
        return context

    @http.route('/qms/order/token/ready', type='json', auth='user')
    def qms_token_ready(self, debug=False, **post):
        context ={}
        qms_token = request.env['qms.token'].sudo().search(['|', '|', ('order_id', '=', post['order_id']), ('session_id', '=', post['session_id']), ('token_number', '=', post['token_number'])], limit=1)
        if qms_token:
            qms_token.sudo().write({'stop_at': fields.Datetime.now(), 'state': 'ready'})
            context.update({
                'qms_token': qms_token[0].name,
                'token_status': qms_token[0].state,
            })
        return context


    @http.route('/qms/order/token/delivery', type='json', auth='user')
    def qms_token_delivery(self, debug=False, **post):
        context ={}
        qms_token = request.env['qms.token'].sudo().search(['|', '|', ('order_id', '=', post['order_id']), ('session_id', '=', post['session_id']), ('token_number', '=', post['token_number'])], limit=1)
        if qms_token:
            qms_token.sudo().write({'state': 'delivered'})
            context.update({
                'qms_token': qms_token[0].name,
                'token_status': qms_token[0].state,
            })
        return context

    @http.route('/qms/web/queue_status', type='http', auth='public')
    def queue_status(self, debug=True, **k):
        context = {}
        
        if 'company_code' in k:
            company_code = k.get('company_code')
            _logger.info('company_code %s', pprint.pformat(company_code))
            company_id = request.env['res.company'].sudo().search([('company_short_code', '=' , company_code)], limit=1).id
            queue_sessions = request.env['qms.session'].sudo().search([('state', '=', 'opened'), ('company_id', '=', company_id)])
            _logger.info('queue_sessions %s', pprint.pformat(queue_sessions))
            if len(queue_sessions) > 0:
                in_process_queue_tokens = request.env['qms.token'].sudo().search([('state', '=', 'progress'), ('session_id', 'in', queue_sessions.ids)]) 
                ready_queue_tokens = request.env['qms.token'].sudo().search([('state', '=', 'ready'), ('session_id', 'in', queue_sessions.ids)])
                context.update({
                'in_progress': in_process_queue_tokens,
                'ready': ready_queue_tokens,
                'company': queue_sessions[0].company_id.id,
                })
        return request.render('fbu_queue_management.queue_status', qcontext=context)
    
    @http.route('/qms/web/queue_status_update', type='json', auth='public')
    def queue_status_update(self, debug=True, **k):
        _logger.info('k %s', pprint.pformat(k))
        context = {}
        if 'company' in k and k.get('company'):
            company = k.get('company')
            queue_sessions = request.env['qms.session'].sudo().search([('state', '=', 'opened'), ('company_id', '=', company)])
            if len(queue_sessions) > 0:
                in_process_queue_tokens = request.env['qms.token'].sudo().search([('state', '=', 'progress'), ('session_id', 'in', queue_sessions.ids)], limit=42, order="id asc") 
                ready_queue_tokens = request.env['qms.token'].sudo().search([('state', '=', 'ready'), ('session_id', 'in', queue_sessions.ids)], limit=42, order="id asc")  
                #_logger.info('pos_sessions feedback with in_process_queue_tokens response data %s', pprint.pformat(in_process_queue_tokens))
                #_logger.info('pos_sessions feedback with ready_queue_tokens response data %s', pprint.pformat(ready_queue_tokens))
                div_ready_list = []
                div_progress_list = []
                if len(ready_queue_tokens) > 0:
                    for ready_queue_token in ready_queue_tokens:
                        div_ready = """
                            <div class="dep_counter">
                                <div class="dep_counter_token_ready">
                                    <div class="counter_tokenno_ready">
                                        """ +str(ready_queue_token.token_number)+ """
                                    </div>
                                </div>
                            </div>
                        """
                        div_ready_list.append(div_ready)
                if len(in_process_queue_tokens) > 0:
                    for in_process_queue_token in in_process_queue_tokens:
                        div_progress = """
                            <div class="dep_counter">
                                <div class="dep_counter_token">
                                    <div class="counter_tokenno_inprogress">
                                        """ +str(in_process_queue_token.token_number)+ """
                                    </div>
                                </div>
                            </div>
                        """
                        div_progress_list.append(div_progress)
                context.update({
                'div_content_ready': div_ready_list,
                'div_content_progress': div_progress_list
                })
        return context
    

    @http.route('/qms/web/close/session/<int:session_id>', type='http', auth='user')
    def qms_web_close(self, session_id, debug=True, **post):
        # if user not logged in, log him in
        pos_order = {}
        pos_session = request.env['qms.session'].search([
            ('state', '=', 'opened'),
            ('id', '=', session_id)], limit=1)
        # _logger.info('pos_sessions feedback with response data %s', pprint.pformat(pos_session))
        # print ('pos_sessions',pos_session)
        if pos_session:
            return werkzeug.utils.redirect('/web#action=fbu_queue_management.action_client_qms_menu')

    