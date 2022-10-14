# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo.tools import float_repr

type_list = {'corporater': 'Corporate', 'distributor': 'Distributor', 'dealer': 'Dealer'}

class SaleBackorderReport(models.AbstractModel):
    _inherit = 'report.olila_reports.sale_backorder_summary_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        selected_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        olila_type = data.get('olila_type')
        partner_id = data.get('partner_id')
        warehouse_ids = data.get('warehouse_ids')
        product_ids = data.get('product_ids')
        partners = self.env['res.partner']

        days_7 = selected_date + relativedelta(days=-7)
        days_10 = days_7 + relativedelta(days=-10)
        days_15 = days_10 + relativedelta(days=-15)
        days_20 = days_15 + relativedelta(days=-20)
        days_30 = days_20 + relativedelta(days=-30)

        if olila_type and not partner_id:
            partners = self.env['res.partner'].sudo().search([('olila_type', '=', olila_type)])
        if partner_id:
            partners = self.env['res.partner'].browse(partner_id)
        if not partners and not olila_type:
            partners = self.env['res.partner'].search([])
        domain = [
            ('partner_id', 'in', partners.ids),
            ('state', 'in', ('confirmed', 'assigned')),
            ('picking_type_code', '=', 'outgoing'),
            ('transfer_id', '=', False),
            ('do_date', '<=', selected_date),
        ]
        if warehouse_ids:
            domain.append(('picking_type_id.warehouse_id', 'in', warehouse_ids))



        delivery_orders = self.env['stock.picking'].search(domain)

        lines = []
        total_day7 = 0
        total_day10 = 0
        total_day15 = 0
        total_day20 = 0
        total_day30 = 0
        total_older_day30 = 0
        grand_total = 0
        for partner in partners:
            # for warehouse in delivery_orders:
            #     wh_orders = delivery_orders.filtered(lambda x: x.picking_type_id.warehouse_id.id == warehouse.id)

            sale_days_7 = delivery_orders.filtered(lambda x: (x.partner_id.id == partner.id) and (
                        x.do_date.date() >= days_7) and (x.do_date.date() <= selected_date))
            sale_days_10 = delivery_orders.filtered(
                lambda x: (x.partner_id == partner) and (x.do_date.date() >= days_10) and (
                            x.do_date.date() <= days_7))
            sale_days_15 = delivery_orders.filtered(
                lambda x: (x.partner_id == partner) and (x.do_date.date() >= days_15) and (
                            x.do_date.date() <= days_10))
            sale_days_20 = delivery_orders.filtered(
                lambda x: (x.partner_id == partner) and (x.do_date.date() >= days_20) and (
                            x.do_date.date() <= days_15))
            sale_days_30 = delivery_orders.filtered(
                lambda x: (x.partner_id == partner) and (x.do_date.date() >= days_30) and (
                            x.do_date.date() <= days_20))
            sale_days_old_30 = delivery_orders.filtered(
                lambda x: (x.partner_id == partner) and (x.do_date.date() <= days_30))


            days_7_qty = 0
            days_10_qty = 0
            days_15_qty = 0
            days_20_qty = 0
            days_30_qty = 0
            days_older_30_qty = 0

            for day7 in sale_days_7:
                for line7 in day7.move_ids_without_package:
                    if line7.product_id.fs_type == 'pcs':
                        days_7_qty = days_7_qty + (line7.product_uom_qty / 72)
                    elif line7.product_id.fs_type == 'inner':
                        days_7_qty = days_7_qty + (line7.product_uom_qty / 12)
                    elif line7.product_id.fs_type == 'master':
                        days_7_qty = days_7_qty + line7.product_uom_qty

            for day10 in sale_days_10:
                for line10 in day10.move_ids_without_package:
                    if line10.product_id.fs_type == 'pcs':
                        days_10_qty = days_10_qty + (line10.product_uom_qty / 72)
                    elif line10.product_id.fs_type == 'inner':
                        days_10_qty = days_10_qty + (line10.product_uom_qty / 12)
                    elif line10.product_id.fs_type == 'master':
                        days_10_qty = days_10_qty + line10.product_uom_qty
            for day15 in sale_days_15:
                for line15 in day15.move_ids_without_package:
                    if line15.product_id.fs_type == 'pcs':
                        days_15_qty = days_15_qty + (line15.product_uom_qty / 72)
                    elif line15.product_id.fs_type == 'inner':
                        days_15_qty = days_15_qty + (line15.product_uom_qty / 12)
                    elif line15.product_id.fs_type == 'master':
                        days_15_qty = days_15_qty + line15.product_uom_qty
            for day20 in sale_days_20:
                for line20 in day20.move_ids_without_package:
                    if line20.product_id.fs_type == 'pcs':
                        days_20_qty = days_20_qty + (line20.product_uom_qty / 72)
                    elif line20.product_id.fs_type == 'inner':
                        days_20_qty = days_20_qty + (line20.product_uom_qty / 12)
                    elif line20.product_id.fs_type == 'master':
                        days_20_qty = days_20_qty + line20.product_uom_qty
            for day30 in sale_days_30:
                for line30 in day30.move_ids_without_package:
                    if line30.product_id.fs_type == 'pcs':
                        days_30_qty = days_30_qty + (line30.product_uom_qty / 72)
                    elif line30.product_id.fs_type == 'inner':
                        days_30_qty = days_30_qty + (line30.product_uom_qty / 12)
                    elif line30.product_id.fs_type == 'master':
                        days_30_qty = days_30_qty + line30.product_uom_qty

            for day31 in sale_days_old_30:
                for line31 in day31.move_ids_without_package:
                    if line31.product_id.fs_type == 'pcs':
                        days_older_30_qty = days_older_30_qty + (line31.product_uom_qty / 72)
                    elif line31.product_id.fs_type == 'inner':
                        days_older_30_qty = days_older_30_qty + (line31.product_uom_qty / 12)
                    elif line31.product_id.fs_type == 'master':
                        days_older_30_qty = days_older_30_qty + line31.product_uom_qty



            days_total = days_7_qty + days_10_qty + days_15_qty + days_20_qty + days_30_qty + days_older_30_qty
            total_day7 = total_day7 + days_7_qty
            total_day10 = total_day10 + days_10_qty
            total_day15 = total_day15 + days_15_qty
            total_day20 = total_day20 + days_20_qty
            total_day30 = total_day30 + days_30_qty
            total_older_day30 = total_older_day30 + days_older_30_qty
            grand_total = grand_total + days_total
            if days_total > 0:
                lines.append({
                    'customer_code': partner.code,
                    'customer_name': partner.name,
                    'warehouse_name': partner.name,
                    'days_7': days_7_qty,
                    'days_10': days_10_qty,
                    'days_15': days_15_qty,
                    'days_20': days_20_qty,
                    'days_30': days_30_qty,
                    'older_30': days_older_30_qty,
                    'total': days_total,
                })



        return {
            'docs': docs,
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'lines': lines,
            'customer_type': type_list.get(olila_type) or '',
            'grand_total': grand_total,
            'total_day7': total_day7,
            'total_day10': total_day10,
            'total_day15': total_day15,
            'total_day20': total_day20,
            'total_day30' : total_day30,
            'total_older_day30' : total_older_day30,
        }