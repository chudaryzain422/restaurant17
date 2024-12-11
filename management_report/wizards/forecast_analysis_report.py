# -*- coding: utf-8 -*-
#############################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2023-TODAY Cybrosys Technologies(<https://www.cybrosys.com>).
#    Author: Raveena V (odoo@cybrosys.com)
#
#    You can modify it under the terms of the GNU AFFERO
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
#############################################################################
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ForecastAnalysisReportWizard(models.TransientModel):
    _name = 'forecast.analysis.report'
    _description = 'Forecast Analysis Report'


    period = fields.Selection([('1week', 'Last 1 week'),
                               ('2week', 'Last 2 weeks'),
                               ('3week', 'Last 3 weeks'),
                               ('1month', 'Last 1 month'),
                               ('2months', 'Last 2 months'),
                               ('3months', 'Last 3 months'),
                               ('6months', 'Last 6 months'),
                               ('12months', 'Last 12 months'),
                               ('24months', 'Last 24 months'),
                               ('36months', 'Last 36 months'),
                               ], string='Duration', required=True,
                              default='3months',
                              help="The duration of the report. 3 months is "
                                   "the default duration")
    start_date = fields.Date(string="Start date")
    end_date = fields.Date(string="End date")

    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)


    # company_id = fields.Many2one('res.company',
    #                              default=lambda self: self.env.company,
    #                              string="Company",
    #                              help="Company of the Product belongs to.")
    growth_rate = fields.Char(string="Growth Rate")


    def action_generate_report(self):
        """ """

        if self.start_date and self.end_date:

          self.env['inventory.forecast'].sudo().train_model(self.company_id.id,self.start_date,self.end_date,self.growth_rate)
          action = self.env['ir.actions.act_window']._for_xml_id('management_report.action_inventory_forecast')
          # action['domain'] = [('source_id', '=', self.source_id.id)]
          # action['context'] = {'create': False}
          return action
        # action = {
        #     'type': 'ir.actions.act_window',
        #     'view_mode': 'tree',
        #     'res_model': 'mailing.mailing',
        #     'res_id': mass_mailing_copy.id,
        #     'context': context,
        # }




    def get_start_date(self, today):
        """This function will calculate the start_date with respect to the
        period and returns the result"""
        res = fields.Date.subtract(today, months=3)
        if self.period == '1week':
            res = fields.Date.subtract(today, weeks=1)
        elif self.period == '2week':
            res = fields.Date.subtract(today, weeks=2)
        elif self.period == '3week':
            res = fields.Date.subtract(today, weeks=3)
        elif self.period == '1month':
            res = fields.Date.subtract(today, months=1)
        elif self.period == '6months':
            res = fields.Date.subtract(today, months=6)
        elif self.period == '12months':
            res = fields.Date.subtract(today, months=12)
        elif self.period == '24months':
            res = fields.Date.subtract(today, months=24)
        elif self.period == '36months':
            res = fields.Date.subtract(today, months=36)
        elif self.period == '2months':
            res = fields.Date.subtract(today, months=2)
        elif self.period == '5months':
            res = fields.Date.subtract(today, months=5)
        return res


