# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta

class OpeningStockReport(models.AbstractModel):
    _inherit = 'report.olila_distribution_dashboard.opening_stock_template'

    def _get_report_values(self, docids, data=None):
        warehouse_name = ['Factory Depot', 'Dhaka Depot', 'Bogra Depot', 'Jashore Depot', 'Hathajari Depot']
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date = data.get('date')
        sale_type = data.get('sale_type')
        product_ids = data.get('product_ids')
        warehouse_ids = self.env['stock.warehouse'].browse(data['warehouse_ids'])

        if not product_ids:
            product_ids = self.env['product.product'].search([('fs_type', '=', 'master')],order='default_code asc').mapped('id')

        if not warehouse_ids:
            warehouse_ids = self.env['stock.warehouse'].search([('name', 'in', warehouse_name)])

        wh_data = []
        for wh in warehouse_ids:
            wh_data.append('Stock')
            wh_data.append('Un.Delivery')

        domain = [('distribution_id.date', '<=', date)]
        if product_ids:
            domain.append(('product_id', 'in', product_ids))
        if sale_type:
            domain.append(('picking_id.sale_type', '=', sale_type))
        if warehouse_ids:
            domain.append(('picking_id.location_id.wh_id', 'in', warehouse_ids.ids))

        dist_lines = self.env['distribution.product.line'].search(domain)
        lines = []

        # get done moves of last day
        selected_date = datetime.strptime(date, '%Y-%m-%d').date()
        last_day = selected_date + timedelta(days=-1)

        last_day_domain = [
            ('date', '>=', last_day), ('date', '<=', last_day),
            ('sale_line_id', '!=', False),
            ('state', '=', 'done'),
        ]
        if product_ids:
            last_day_domain.append(('product_id', 'in', product_ids))
        if sale_type:
            last_day_domain.append(('picking_id.sale_type', '=', sale_type))
        if warehouse_ids:
            last_day_domain.append(('picking_id.location_id.wh_id', 'in', warehouse_ids.ids))
        last_day_moves = self.env['stock.move'].search(last_day_domain)

        out_moves = dist_lines.mapped('picking_id.move_lines') + last_day_moves
        if product_ids:
            out_moves = out_moves.filtered(lambda x: x.product_id.id in product_ids)
        group_by_product = {}
        for move in out_moves:
            if move.product_id in group_by_product:
                group_by_product[move.product_id] |= move
            else:
                group_by_product[move.product_id] = move

        for product_id in product_ids:
            if product_id not in out_moves.mapped('product_id').ids:
                product = self.env['product.product'].browse(product_id)
                group_by_product[product] = self.env['stock.move']

        sr_no = 1
        wh_total = {}
        footer_total = {}
        footer_total_gross_stock = 0.0
        footer_total_undel_retail = 0.0
        footer_total_undel_corp = 0.0
        footer_total_undelivered = 0.0
        footer_last_day_del_retail = 0.0
        footer_last_day_del_corp = 0.0
        footer_total_delivery = 0.0
        footer_last_day_do = 0.0
        footer_net_stock = 0.0
        for warehouse in warehouse_ids:
            footer_total[warehouse.name] = {'wh_total_stock': 0.0, 'total_stock': 0.0}
        for product_id, moves in group_by_product.items():
            wh_stock = []
            total_stock = 0.0
            total_undel_retail = 0
            total_undel_corp = 0
            for wh in warehouse_ids:
                moves = self.env['stock.move'].search([('state', 'in', ('confirmed', 'assigned','partially_available')),
                                                          ('location_id','=', wh.lot_stock_id.id), ('product_id','=',product_id.id)])
                undel_retail = 0
                undel_corp = 0
                qty = 0
                for move in moves:
                    if move.picking_id.sale_type:
                        qty += move.product_uom_qty
                        if move.picking_id.sale_type == 'primary_sales':
                            undel_retail +=  move.product_uom_qty
                        elif move.picking_id.sale_type == 'corporate_sales':
                            undel_corp += move.product_uom_qty
                available_qty = self.env['stock.quant'].search([('product_id', '=',product_id.id),('location_id', '=',wh.lot_stock_id.id)],limit =1).quantity
                wh_stock.append({
                    'stock': available_qty,
                    'qty': qty,
                })
                if wh.name not in footer_total:
                    footer_total[wh.name] = {'wh_total_stock': round(available_qty, 2), 'total_stock': round(qty, 2)}
                else:
                    footer_total[wh.name]['wh_total_stock'] += round(available_qty, 2)
                    footer_total[wh.name]['total_stock'] += round(qty, 2)
                total_stock += available_qty
                if wh in wh_total:
                    wh_total[wh] = wh_total[wh] + qty
                else:
                    wh_total[wh] = qty
                # retail_moves = moves.filtered(lambda x: x.picking_id.sale_type == 'primary_sales')
                # corporate_moves = moves.filtered(lambda x: x.picking_id.sale_type == 'corporate_sales')
                total_undel_retail += undel_retail
                total_undel_corp += undel_corp
                total_undelivered = total_undel_retail + total_undel_corp
                net_stock = total_stock - total_undelivered
                last_day_del_retail = sum(last_day_moves.filtered(lambda x: x.product_id.id == product_id.id and x.picking_id.sale_type == 'primary_sales').mapped('quantity_done'))
                last_day_del_corp = sum(last_day_moves.filtered(lambda x: x.product_id.id == product_id.id and x.picking_id.sale_type == 'corporate_sales').mapped('quantity_done'))
                total_delivery = last_day_del_retail + last_day_del_corp
                last_day_do = len(last_day_moves.filtered(lambda x: x.product_id.id == product_id.id and x.picking_id.sale_type != False).mapped('picking_id'))
            footer_total_gross_stock += total_stock
            footer_total_undel_retail += total_undel_retail
            footer_total_undel_corp += total_undel_corp
            footer_total_undelivered += total_undelivered
            footer_last_day_del_retail += last_day_del_retail
            footer_last_day_del_corp += last_day_del_corp
            footer_total_delivery += total_delivery
            footer_last_day_do += last_day_do
            footer_net_stock += net_stock
            lines.append({
                'sr_no': sr_no,
                'code': product_id.default_code,
                'product': product_id.name,
                'wh_stock': wh_stock,
                'total_stock': total_stock,
                'total_undel_retail': total_undel_retail,
                'total_undel_corp': total_undel_corp,
                'total_undelivered': total_undelivered,
                'last_day_del_retail': last_day_del_retail,
                'last_day_del_corp': last_day_del_corp,
                'total_delivery': total_delivery,
                'last_day_do': last_day_do,
                'net_stock': net_stock,
            })
            sr_no += 1
        footer_total.update({
            'footer_total_gross_stock':  round(footer_total_gross_stock, 2),
            'footer_total_undel_retail': round(footer_total_undel_retail, 2),
            'footer_total_undel_corp': round(footer_total_undel_corp, 2),
            'footer_total_undelivered': round(footer_total_undelivered, 2),
            'footer_last_day_del_retail': round(footer_last_day_del_retail, 2),
            'footer_last_day_del_corp': round(footer_last_day_del_corp, 2),
            'footer_total_delivery': round(footer_total_delivery, 2),
            'footer_last_day_do': round(footer_last_day_do, 2),
            'footer_net_stock': round(footer_net_stock, 2),
        })
        print('lines', lines)
        return {
            'docs': docs,
            'warehouse': warehouse_ids.mapped('name'),
            'wh_data': wh_data,
            'lines': sorted(lines, key=lambda l: l['code']),
            'wh_header': ', '.join(warehouse_ids.mapped('name')),
            'footer_total': footer_total,
        }