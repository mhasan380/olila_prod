# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.tools import float_repr

type_list = {'corporater': 'Corporate', 'distributor': 'Distributor', 'dealer': 'Dealer'}

class CustomerOutstandingSummaryReport(models.AbstractModel):
    _inherit = 'report.olila_reports.customer_outstanding_summary_template'

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
        days_90 = days_60 + relativedelta(days=-15)

        if olila_type and not partner_id:
            partners = self.env['res.partner'].sudo().search([('olila_type', '=', olila_type)])
        if partner_id:
            partners = self.env['res.partner'].browse(partner_id)
        if not partners and not olila_type:
            partners = self.env['res.partner'].search([])

        invoice_line_ids = self.env['account.move.line'].search([
            ('partner_id', 'in', partners.ids),
            ('move_id.state', '=', 'posted'),
            ('account_id.user_type_id', '=', 'Receivable')
        ])
        invoice_ids = invoice_line_ids
        print(invoice_ids)

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
                lambda x: (x.partner_id.id == partner.id) and (x.date >= days_15) and (
                            x.date <= selected_date))
            invoice_30 = invoice_ids.filtered(
                lambda x: (x.partner_id.id == partner.id) and (x.date >= days_30) and (x.date <= days_15))
            invoice_45 = invoice_ids.filtered(
                lambda x: (x.partner_id.id == partner.id) and (x.date >= days_45) and (x.date <= days_30))
            invoice_60 = invoice_ids.filtered(
                lambda x: (x.partner_id.id == partner.id) and (x.date >= days_60) and (x.date <= days_45))
            invoice_90 = invoice_ids.filtered(
                lambda x: (x.partner_id.id == partner.id) and (x.date >= days_90) and (x.date <= days_60))
            invoice_old_90 = invoice_ids.filtered(lambda x: (x.partner_id.id == partner.id) and (x.date <= days_90))
            days_15_amt = sum(invoice_15.mapped('debit')) - sum(invoice_15.mapped('credit'))
            days_30_amt = sum(invoice_30.mapped('debit')) - sum(invoice_30.mapped('credit'))
            days_45_amt = sum(invoice_45.mapped('debit')) - sum(invoice_45.mapped('credit'))
            days_60_amt = sum(invoice_60.mapped('debit')) - sum(invoice_60.mapped('credit'))
            days_90_amt = sum(invoice_90.mapped('debit')) - sum(invoice_90.mapped('credit'))
            older_90_amt = sum(invoice_old_90.mapped('debit')) - sum(invoice_old_90.mapped('credit'))
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
                    'days_15': round(days_15_amt, 2),
                    'days_30': round(days_30_amt, 2),
                    'days_45':  round(days_45_amt, 2),
                    'days_60': round(days_60_amt, 2),
                    'days_90':  round(days_90_amt, 2),
                    'older_90':  round(older_90_amt, 2),
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