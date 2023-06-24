# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta

class OpeningStockWizard(models.TransientModel):
    _inherit = 'opening.stock.wizard'

    product_category = fields.Many2many('product.category', string="Category")

    def get_xls_report(self):
        if not self.product_ids:
            product_ids = self.env['product.product'].search([('categ_id', 'in', self.product_category.ids)],order='default_code asc').mapped('id')
        if not self.warehouse_ids:
            warehouse_ids = self.env['stock.warehouse'].search([('is_depot', '=', True)])

        wh_data = []
        for wh in warehouse_ids:
            wh_data.append('Stock')
            wh_data.append('Un.Delivery')

        domain = [('distribution_id.date', '<=', date)]
        if self.product_ids:
            domain.append(('product_id', 'in', self.product_ids))
        if self.sale_type:
            domain.append(('picking_id.sale_type', '=', self.sale_type))
        if self.warehouse_ids:
            domain.append(('picking_id.location_id.wh_id', 'in', self.warehouse_ids.ids))

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
        if self.product_ids:
            last_day_domain.append(('product_id', 'in', self.product_ids))
        if self.sale_type:
            last_day_domain.append(('picking_id.sale_type', '=', self.sale_type))
        if self.warehouse_ids:
            last_day_domain.append(('picking_id.location_id.wh_id', 'in', self.warehouse_ids.ids))
        last_day_moves = self.env['stock.move'].search(last_day_domain)

        out_moves = dist_lines.mapped('picking_id.move_lines') + last_day_moves
        if self.product_ids:
            out_moves = out_moves.filtered(lambda x: x.product_id.id in self.product_ids)
        group_by_product = {}
        for move in out_moves:
            if move.product_id in group_by_product:
                group_by_product[move.product_id] |= move
            else:
                group_by_product[move.product_id] = move

        for product_id in self.product_ids:
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
            for wh in warehouse_ids:
                moves = moves.filtered(lambda x: x.state not in ('done', 'cancel'))
                qty = sum(moves.filtered(lambda x: x.location_id.wh_id.id == wh.id).mapped('product_uom_qty'))
                available_qty = product_id.with_context(warehouse=wh.id).qty_available
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
                retail_moves = moves.filtered(lambda x: x.picking_id.sale_type == 'primary_sales')
                corporate_moves = moves.filtered(lambda x: x.picking_id.sale_type == 'corporate_sales')
                total_undel_retail = sum(retail_moves.mapped('product_uom_qty'))
                total_undel_corp = sum(corporate_moves.mapped('product_uom_qty'))
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
        print('ddddddddddddddd', footer_total)
        return {
            'warehouse': warehouse_ids.mapped('name'),
            'wh_data': wh_data,
            'lines': lines,
            'wh_header': ', '.join(warehouse_ids.mapped('name')),
            'footer_total': footer_total,
        }