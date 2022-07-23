# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import float_repr

type_list = {'corporater': 'Corporate', 'distributor': 'Distributor', 'dealer': 'Dealer'}


class CustomerOutstandingWizard(models.TransientModel):
    _name = 'customer.outstanding.wizard'

    date = fields.Date(string="Date", required=True)
    olila_type = fields.Selection([('corporater', 'Corporate'), ('dealer', 'Dealer'), ('distributor', 'Distributor')],
                                  string="Customer Type")
    partner_id = fields.Many2one('res.partner', string='Customer Name')
    report_type = fields.Selection([('summary', 'Summary'), ('details', 'Details')], default='summary', required=True)

    def action_print_report(self):
        data = {
            'date': self.date,
            'olila_type': self.olila_type or False,
            'partner_id': (self.partner_id and self.partner_id.id) or False
        }
        if self.report_type == 'summary':
            return self.env.ref('customer_details_report.customer_out_summary_report').report_action(self,
                                                                                                     data=data)
        else:
            return self.env.ref('customer_details_report.customer_out_details_report').report_action(self,
                                                                                                     data=data)


class CustomerOutstandingSummaryReport(models.AbstractModel):
    _name = 'report.customer_details_report.customer_out_summary_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        selected_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        olila_type = data.get('olila_type')
        partner_id = data.get('partner_id')
        partners = self.env['res.partner']

        days_15 = selected_date + relativedelta(days=-15)
        days_30 = days_15 + relativedelta(days=-15)
        days_45 = days_30 + relativedelta(days=-15)
        days_60 = days_45 + relativedelta(days=-15)
        days_90 = days_60 + relativedelta(days=-30)

        if olila_type and not partner_id:
            partners = self.env['res.partner'].sudo().search([('olila_type', '=', olila_type)])
        if partner_id:
            partners = self.env['res.partner'].browse(partner_id)
        if not partners and not olila_type:
            partners = self.env['res.partner'].search([])

        invoice_line_ids = self.env['account.move.line'].search([
            ('move_id.partner_id', 'in', partners.ids),
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', '=', 'out_invoice'),
            ('sale_line_ids', '!=', False),
            ('move_id.amount_residual', '>', 0),
        ])
        invoice_ids = invoice_line_ids.mapped('move_id')

        lines = []
        footer_total = {}
        total_15 = 0.0
        total_30 = 0.0
        total_45 = 0.0
        total_60 = 0.0
        total_90 = 0.0
        total_older_90 = 0.0
        grand_total = 0.0
        for partner in partners:
            invoice_15 = invoice_ids.filtered(
                lambda x: (x.partner_id.id == partner.id) and (x.invoice_date >= days_15) and (
                        x.invoice_date <= selected_date))
            invoice_30 = invoice_ids.filtered(
                lambda x: (x.partner_id == partner) and (x.invoice_date >= days_30) and (x.invoice_date <= days_15))
            invoice_45 = invoice_ids.filtered(
                lambda x: (x.partner_id == partner) and (x.invoice_date >= days_45) and (x.invoice_date <= days_30))
            invoice_60 = invoice_ids.filtered(
                lambda x: (x.partner_id == partner) and (x.invoice_date >= days_60) and (x.invoice_date <= days_45))
            invoice_90 = invoice_ids.filtered(
                lambda x: (x.partner_id == partner) and (x.invoice_date >= days_90) and (x.invoice_date <= days_60))
            invoice_old_90 = invoice_ids.filtered(lambda x: (x.partner_id == partner) and (x.invoice_date <= days_90))
            days_15_amt = sum(invoice_15.mapped('amount_residual'))
            days_30_amt = sum(invoice_30.mapped('amount_residual'))
            days_45_amt = sum(invoice_45.mapped('amount_residual'))
            days_60_amt = sum(invoice_60.mapped('amount_residual'))
            days_90_amt = sum(invoice_90.mapped('amount_residual'))
            older_90_amt = sum(invoice_old_90.mapped('amount_residual'))
            summary_total = days_15_amt + days_30_amt + days_45_amt + days_60_amt + days_90_amt + older_90_amt
            if summary_total > 0:
                total_15 += days_15_amt
                total_30 += days_30_amt
                total_45 += days_45_amt
                total_60 += days_60_amt
                total_90 += days_90_amt
                total_older_90 += older_90_amt
                grand_total += summary_total
                lines.append({
                    'code': partner.code,
                    'name': partner.name,
                    'days_15': days_15_amt,
                    'days_30': days_30_amt,
                    'days_45': days_45_amt,
                    'days_60': days_60_amt,
                    'days_90': days_90_amt,
                    'older_90': older_90_amt,
                    'total': float_repr(summary_total, precision_digits=2),
                })
        footer_total = {'total_15': round(total_15, 2), 'total_30': round(total_30, 2), 'total_45': round(total_45, 2),
                        'total_60': round(total_60, 2), 'total_90': round(total_90, 2),
                        'total_older_90': round(total_older_90, 2), 'grand_total': round(grand_total, 2)}
        return {
            'docs': docs,
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'lines': lines,
            'footer_total': footer_total,
            'customer_type': type_list.get(olila_type) or '',
        }


class CustomerOutstandingDetailsReport(models.AbstractModel):
    _name = 'report.customer_details_report.customer_out_details_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        selected_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        olila_type = data.get('olila_type')
        partner_id = data.get('partner_id')
        partners = self.env['res.partner']

        date_15 = selected_date + relativedelta(days=-15)
        date_30 = date_15 + relativedelta(days=-15)
        date_45 = date_30 + relativedelta(days=-15)
        date_60 = date_45 + relativedelta(days=-15)
        date_90 = date_60 + relativedelta(days=-15)

        if olila_type and not partner_id:
            partners = self.env['res.partner'].sudo().search([('olila_type', '=', olila_type)])
        if partner_id:
            partners = self.env['res.partner'].browse(partner_id)
        if not partners and not olila_type:
            partners = self.env['res.partner'].search([])

        invoice_line_ids = self.env['account.move.line'].search([
            ('move_id.partner_id', 'in', partners.ids),
            ('move_id.state', '=', 'posted'),
            ('move_id.move_type', '=', 'out_invoice'),
            ('sale_line_ids', '!=', False),
            ('move_id.amount_residual', '>', 0),
        ])
        sale_orders = invoice_line_ids.mapped('sale_line_ids.order_id')

        lines = []
        footer_total = {}
        total_15 = 0.0
        total_30 = 0.0
        total_45 = 0.0
        total_60 = 0.0
        total_90 = 0.0
        total_older_90 = 0.0
        grand_total = 0.0
        for partner in partners:
            for inv in invoice_line_ids.mapped('move_id').filtered(lambda x: x.partner_id == partner):
                days_15 = inv.amount_residual if (inv.invoice_date > date_15) and (
                        inv.invoice_date <= selected_date) else 0
                days_30 = inv.amount_residual if (inv.invoice_date > date_30) and (inv.invoice_date <= date_15) else 0
                days_45 = inv.amount_residual if (inv.invoice_date > date_45) and (inv.invoice_date <= date_30) else 0
                days_60 = inv.amount_residual if (inv.invoice_date > date_60) and (inv.invoice_date <= date_45) else 0
                days_90 = inv.amount_residual if (inv.invoice_date > date_90) and (inv.invoice_date <= date_60) else 0
                older_90 = inv.amount_residual if inv.invoice_date <= date_90 else 0
                days_total = days_15 + days_30 + days_45 + days_60 + days_90 + older_90
                if days_total > 0:
                    total_15 += days_15
                    total_30 += days_30
                    total_45 += days_45
                    total_60 += days_60
                    total_90 += days_90
                    total_older_90 += older_90
                    grand_total += days_total
                    lines.append({
                        'code': partner.code,
                        'name': partner.name,
                        'invoice': inv.name,
                        'sale_order': ','.join(inv.invoice_line_ids.mapped('sale_line_ids.order_id.name')),
                        'days_15': days_15,
                        'days_30': days_30,
                        'days_45': days_45,
                        'days_60': days_60,
                        'days_90': days_90,
                        'older_90': older_90,
                        'total': float_repr(days_total, precision_digits=2),
                    })
        footer_total = {'total_15': round(total_15, 2), 'total_30': round(total_30, 2), 'total_45': round(total_45, 2),
                        'total_60': round(total_60, 2), 'total_90': round(total_90, 2),
                        'total_older_90': round(total_older_90, 2), 'grand_total': round(grand_total, 2)}

        return {
            'docs': docs,
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'lines': lines,
            'footer_total': footer_total,
            'customer_type': type_list.get(olila_type) or '',
        }
