# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError


class QMSSession(models.Model):
    _name = 'qms.session'
    _order = 'id desc'

    QUE_SESSION_STATE = [
        ('opening_control', 'Opening Control'),  # method action_pos_session_open
        ('opened', 'In Progress'),               # method action_pos_session_closing_control
        ('closing_control', 'Closing Control'),  # method action_pos_session_close
        ('closed', 'Closed & Posted'),
    ]

    name = fields.Char(string='Session ID', required=True, readonly=True, default='/')
    user_id = fields.Many2one(
        'res.users', string='Responsible',
        required=True,
        index=True,
        readonly=True,
        states={'opening_control': [('readonly', False)]},
        default=lambda self: self.env.uid)
    start_at = fields.Datetime(string='Opening Date', readonly=True)
    stop_at = fields.Datetime(string='Closing Date', readonly=True, copy=False)
    company_id = fields.Many2one('res.company', string='Company', change_default=True,
        required=True, default=lambda self: self.env['res.company']._company_default_get('qms.session'))
    state = fields.Selection(
        QUE_SESSION_STATE, string='Status',
        required=True, readonly=True,
        index=True, copy=False, default='opening_control')

    token_ids = fields.One2many('qms.token', 'session_id',  string='Tokens')
    _sql_constraints = [('uniq_name', 'unique(name)', "The name of this QMS Session must be unique !")]


    @api.constrains('user_id', 'state')
    def _check_unicity(self):
        # open if there is no session in 'opening_control', 'opened', 'closing_control' for one user
        if self.search_count([
                ('state', 'not in', ('closed', 'closing_control')),
                ('user_id', '=', self.user_id.id),
            ]) > 1:
            raise ValidationError(_("You cannot create two active sessions with the same responsible!"))



    def unlink(self):
        return super(QMSSession, self).unlink()


    def open_frontend_cb(self):
        if not self.ids:
            return {}
        for session in self.filtered(lambda s: s.user_id.id != self.env.uid):
            raise UserError(_("You cannot use the session of another user. This session is owned by %s. "
                              "Please first close this one to use this point of sale.") % session.user_id.name)
        return {
            'type': 'ir.actions.act_url',
            'target': 'self',
            'url':   '/qms/web/queue_ticket',
        }

    def action_qms_session_open(self):
        # we only open sessions that haven't already been opened
        for session in self.filtered(lambda session: session.state == 'opening_control'):
            values = {}
            if not session.start_at:
                values['start_at'] = fields.Datetime.now()
            values['state'] = 'opened'
            session.write(values)
        return True

    @api.model
    def create(self, values):
        
        qms_name = self.env['ir.sequence'].with_context({}).next_by_code('qms.session')
        if values.get('name'):
            qms_name += ' ' + values['name']

        values.update({
            'name': qms_name,
        })
        res = super(QMSSession, self.with_context({})).create(values)
        res.action_qms_session_open()
        return res


    def action_qms_session_closing_control(self):
        for session in self:
            session.write({'state': 'closing_control', 'stop_at': fields.Datetime.now()})
            for token in session.token_ids:
                token.sudo().write({'state': 'delivered'})
            session.action_qms_session_close()

    def action_qms_session_close(self):
        # Close CashBox
        self.write({'state': 'closed'})
        return {
            'type': 'ir.actions.client',
            'name': 'Queue Management Menu',
            'tag': 'reload',
            'params': {'menu_id': self.env.ref('fbu_queue_management.menu_qms_root').id},
        }
    