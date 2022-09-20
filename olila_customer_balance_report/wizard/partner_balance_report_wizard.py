# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils
from datetime import datetime, timedelta

class PartnerBalanceReportWizard(models.TransientModel):
    _name = 'partner.balance.report.wizard'

    customer_id = fields.Many2one('res.partner', 'Customer')
    customer_type = fields.Selection([('corporater', 'Corporate'), ('dealer', 'Dealer'), ('distributor', 'Distributor')], string="Customer Type")



    def get_report(self):
        today = fields.Date.today()
        customer_id = self.customer_id

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'customer_id':customer_id.id,
                'customer_type': self.customer_type,
            },
        }
        return self.env.ref('olila_customer_balance_report.partner_balance_report').report_action(self, data=data)




class PartnerBalanceReport(models.AbstractModel):

    _name = 'report.olila_customer_balance_report.partner_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        customer_type = data['form']['customer_type']
        customer_id = data['form']['customer_id']
        customer_name = self.env['res.partner'].browse(customer_id)

        customer_balance_dict = {}

        if customer_type:
            customers = self.env['res.partner'].search([('is_customer', '=', True),('olila_type', '=', customer_type)])
            if customer_id:
                customers = self.env['res.partner'].search(
                    [('id', '=', customer_id)])
        else:
            customers = self.env['res.partner'].search([('is_customer', '=', True)])

        for customer in customers:
            customer_balance = 0
            journals = self.env['account.move.line'].search([('partner_id', '=', customer.id)])
            for line in journals:
                if (line.account_id.user_type_id.display_name == 'Receivable') and (line.move_id.state == 'posted'):
                    customer_balance = customer_balance + line.debit - line.credit
            if customer_balance != 0:
                customer_balance_dict.setdefault(customer, {'customer_code': customer.code,
                                                        'customer_name': customer.name,
                                                        'customer_balance': customer_balance,
                                                         })



        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'customer_balance_dict': list(customer_balance_dict.values()),
             'customer_name': customer_name

            }

