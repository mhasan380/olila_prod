# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_repr
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
type_list = {'corporater': 'Corporate', 'distributor': 'Distributor', 'dealer': 'Dealer'}

class SaleSummaryRegionWiseReport(models.AbstractModel):
    _inherit = 'report.olila_reports.sale_summary_region_wise_template'

    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = data['date_from']
        date_to = data['date_to']
        olila_type = data.get('olila_type')
        partner_id = data.get('partner_id')
        zone_ids = data.get('zone_ids')
        product_ids = data.get('product_ids')
        partners = self.env['res.partner']

        if olila_type and not partner_id:
            partners = self.env['res.partner'].sudo().search([('olila_type', '=', olila_type)])
        if partner_id:
            partners = self.env['res.partner'].browse(partner_id)
        if not partners and not olila_type:
            partners = self.env['res.partner'].search([])

        domain = [('partner_id', 'in', partners.ids),('date_order','>=',date_from),('date_order','<=',date_to)]
        if zone_ids:
            domain.append(('zone_id', 'in', zone_ids))
        sale_orders = self.env['sale.order'].search(domain)

        lines = []
        total_qty = 0.0
        total_invoice_value = 0.0
        for zone in sale_orders.mapped('zone_id'):
            zone_orders = sale_orders.filtered(lambda x: x.zone_id == zone)
            zone_lines = zone_orders.mapped('order_line')
            if product_ids:
                zone_lines = zone_lines.filtered(lambda x: x.product_id.id in product_ids)
            product_by_lines = self._get_lines_by_product(zone_lines)
            for product, o_lines in product_by_lines.items():
                subtotal = sum(o_lines.mapped('price_subtotal'))
                invoice_value = subtotal + (subtotal * 0.15)
                lines.append({
                    'zone': zone.name,
                    'product_code': product.default_code or '',
                    'product_name': product.name,
                    'product_qty': sum(o_lines.mapped('product_uom_qty')),
                    'invoice_value': invoice_value
                })
                total_qty += sum(o_lines.mapped('product_uom_qty'))
                total_invoice_value += invoice_value

        return {
            'docs': docs,
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'lines':lines,
            'total_qty': round(total_qty, 2),
            'total_invoice_value': round(total_invoice_value, 2),
            'customer_type': type_list.get(olila_type) or '',
            'customer_name': self.env['res.partner'].browse(data.get('partner_id')).name or '',
        }


class SaleSummaryCustomerWiseReport(models.AbstractModel):
    _inherit = 'report.olila_reports.sale_summary_customer_wise_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = data['date_from']
        date_to = data['date_to']
        olila_type = data.get('olila_type')
        partner_id = data.get('partner_id')
        partners = self.env['res.partner']
        if olila_type and not partner_id:
            partners = self.env['res.partner'].sudo().search([('olila_type', '=', olila_type)])
        if partner_id:
            partners = self.env['res.partner'].browse(partner_id)
        if not partners and not olila_type:
            partners = self.env['res.partner'].search([])

        sale_orders = self.env['sale.order'].search(
            [('state', 'in', ('sale', 'done')), ('partner_id', 'in', partners.ids), ('date_order', '>=', date_from),
             ('date_order', '<=', date_to)])
        lines = []
        total_invoice = 0.0
        total_sale = 0.0
        total_undelivered = 0.0
        for sale in sale_orders:
            undelivered = 0
            for line in sale.order_line:
                if line.qty_delivered > 0:
                    undelivered_qty = (line.product_uom_qty - line.qty_delivered)
                    undelivered += (
                                               line.price_total / line.product_uom_qty) * undelivered_qty if line.product_uom_qty > 0 else 0.0
                else:
                    undelivered += line.price_total
            lines.append({
                'customer_code': sale.partner_id.code,
                'customer_name': sale.partner_id.name,
                'sale_no': sale.name,
                'invoice_no': ', '.join(sale.invoice_ids.mapped('name')),
                'invoice_value': sum(sale.invoice_ids.mapped('amount_total')),
                'sale_date': sale.date_order and self._get_client_time(sale.date_order) or '',
                'sale_value': sale.amount_total,
                'undelivered': undelivered,
            })
            total_invoice += sum(sale.invoice_ids.mapped('amount_total'))
            total_sale += sale.amount_total
            total_undelivered += undelivered

        footer_total = {'total_invoice': total_invoice, 'total_sale': total_sale,
                        'total_undelivered': total_undelivered}
        return {
            'docs': docs,
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'lines': lines,
            'footer_total': footer_total,
            'customer_type': type_list.get(olila_type) or '',
            'customer_name': self.env['res.partner'].browse(data.get('partner_id')).name or '',
        }