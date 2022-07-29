# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from odoo.tools import float_repr
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz

type_list = {'corporater': 'Corporate', 'distributor': 'Distributor', 'dealer': 'Dealer'}


class CustomerOutstandingSummaryWizard(models.TransientModel):
    _inherit = 'sales.status.wizard'

    sale_type = fields.Selection(
        [('primary_sales', 'Primary Sales'), ('corporate_sales', 'Corporate Sales')],
        default='primary_sales')
    def action_print_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'olila_type': self.olila_type or False,
            'partner_id': self.partner_id and self.partner_id.id or False,
            'sale_type' : self.sale_type
        }
        return self.env.ref('olila_reports.sales_status_report').report_action(self, data=data)


class SaleStatusReport(models.AbstractModel):
    _inherit = 'report.olila_reports.sales_status_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = data['date_from']
        date_to = data['date_to']
        olila_type = data.get('olila_type')
        partner_id = data.get('partner_id')
        sale_type = data.get('sale_type')
        partners = self.env['res.partner']
        if sale_type and not partner_id:
            sale_orders = self.env['sale.order'].search(
                [('sale_type', '=', sale_type), ('date_order', '>=', date_from), ('date_order', '<=', date_to)])
        if partner_id:
            sale_orders = self.env['sale.order'].search(
                [('partner_id', 'in', partners.ids), ('date_order', '>=', date_from), ('date_order', '<=', date_to)])
        if not partner_id and not sale_type:
            sale_orders = self.env['sale.order'].search(
                [('date_order', '>=', date_from), ('date_order', '<=', date_to)])


        sale_status = {
            'draft': 'Quotation',
            'sent': 'Quotation Sent',
            'sale': 'Sale Order',
            'done': 'Locked',
            'cancel': 'Cancelled',
            'waiting_for_approval': 'Waiting For Approval',
            'waiting_for_final_approval': 'Final Approval',
        }
        lines = []
        total_net_value = 0.0
        for sale in sale_orders:
            total_net_value += sale.amount_total
            lines.append({
                'name': sale.name,
                'date_order': sale.date_order and self._get_client_time(sale.date_order) or '',
                'customer_code': sale.partner_id.code,
                'customer_name': sale.partner_id.name,
                'net_value': sale.amount_total,
                'status': sale_status.get(sale.state, ' '),
                'auth_status': 'Pending' if sale.state in (
                'waiting_for_final_approval', 'waiting_for_approval') else 'Done'
            })
        return {
            'docs': docs,
            'lines': lines,
            'total_net_value': total_net_value,
            'customer_type': type_list.get(olila_type) or '',
        }