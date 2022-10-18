# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
from odoo.tools import float_repr
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
import pytz
type_list = {'corporater': 'Corporate', 'distributor': 'Distributor', 'dealer': 'Dealer'}

class SaleSummaryWizard(models.TransientModel):
    _inherit = 'sale.summary.wizard'
    sort_type = fields.Selection([('asc', 'Ascending'), ('desc', 'Descending')], string='Sort Type')
    sale_type = fields.Selection(
        [('primary_sales', 'Primary Sales'), ('corporate_sales', 'Corporate Sales'), ('all', 'All Sales')],
        default='primary_sales')
    def action_print_report(self):
        data = {
            'date_from': self.date_from,
            'date_to': self.date_to,
            'olila_type': self.olila_type or False,
            'partner_id': self.partner_id and self.partner_id.id or False,
            'zone_ids': self.zone_ids.ids,
            'product_ids': self.product_ids.ids,
            'sort_type' : self.sort_type,
            'sale_type': self.sale_type
        }
        if self.report_type == 'customer':
            return self.env.ref('olila_reports.sale_summary_customer_wise_report').report_action(self, data=data)
        if self.report_type == 'product':
            return self.env.ref('olila_reports.sale_summary_product_wise_report').report_action(self, data=data)
        if self.report_type == 'region':
            return self.env.ref('olila_reports.sale_summary_region_wise_report').report_action(self, data=data)

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
        sort_type = data.get('sort_type')
        partners = self.env['res.partner']
        print(product_ids)

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

        if sort_type == 'desc':
            return {
                'docs': docs,
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),
                'lines': sorted(lines, key=lambda l: l['invoice_value'],reverse= True),
                'total_qty': round(total_qty, 2),
                'total_invoice_value': round(total_invoice_value, 2),
                'customer_type': type_list.get(olila_type) or '',
                'customer_name': self.env['res.partner'].browse(data.get('partner_id')).name or '',
            }
        elif sort_type == 'asc':
            return {
                'docs': docs,
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),
                'lines': sorted(lines, key=lambda l: l['invoice_value']),
                'total_qty': round(total_qty, 2),
                'total_invoice_value': round(total_invoice_value, 2),
                'customer_type': type_list.get(olila_type) or '',
                'customer_name': self.env['res.partner'].browse(data.get('partner_id')).name or '',
            }
        else:
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
        sort_type = data.get('sort_type')
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
        if sort_type == 'desc':
            return {
                'docs': docs,
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),
                'lines': sorted(lines, key=lambda l: l['sale_value'],reverse= True),
                'footer_total': footer_total,
                'customer_type': type_list.get(olila_type) or '',
                'customer_name': self.env['res.partner'].browse(data.get('partner_id')).name or '',
            }
        elif sort_type == 'asc':
            return {
                'docs': docs,
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),
                'lines': sorted(lines, key=lambda l: l['sale_value']),
                'footer_total': footer_total,
                'customer_type': type_list.get(olila_type) or '',
                'customer_name': self.env['res.partner'].browse(data.get('partner_id')).name or '',
            }
        else:
            return {
                'docs': docs,
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),
                'lines': lines,
                'footer_total': footer_total,
                'customer_type': type_list.get(olila_type) or '',
                'customer_name': self.env['res.partner'].browse(data.get('partner_id')).name or '',
            }


class SaleSummaryProductWiseReport(models.AbstractModel):
    _inherit = 'report.olila_reports.sale_summary_product_wise_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date_from = data['date_from']
        date_to = data['date_to']
        olila_type = data.get('olila_type')
        partner_id = data.get('partner_id')
        partners = self.env['res.partner']
        zone_ids = data.get('zone_ids')
        product_ids = data.get('product_ids')
        sale_type = data.get('sale_type')
        sort_type = data.get('sort_type')
        zones = []
        for zone in zone_ids:
            zone_name = self.env['res.zone'].search([('id', '=', zone)]).name
            zones.append(zone_name)

        if olila_type and not partner_id:
            partners = self.env['res.partner'].sudo().search([('olila_type', '=', olila_type)])
        if partner_id:
            partners = self.env['res.partner'].browse(partner_id)
        if not partners and not olila_type:
            partners = self.env['res.partner'].search([])

        domain = [('state', 'in', ('sale', 'done')), ('partner_id', 'in', partners.ids),
                  ('date_order', '>=', date_from), ('date_order', '<=', date_to)]
        if zone_ids:
            domain.append(('zone_id.id', 'in', zone_ids))
        if sale_type == 'primary_sales' or sale_type == 'corporate_sales':
            domain.append(('sale_type', '=', sale_type))

        sale_orders = self.env['sale.order'].search(domain)

        lines = []

        list2 = []
        product_wise_lines = {}
        total_qty = 0.0
        total_invoice_value = 0.0

        if product_ids:
            for line in sale_orders.mapped('order_line'):
                key = (line.product_id.id)
                product_wise_lines.setdefault(key, [])
                if line.product_id.id in product_ids:
                    product_wise_lines[key].append(line)
            for product_id, lines in product_wise_lines.items():
                price_total = 0
                product_subtotal = 0
                price_total_withtax = 0
                product = self.env['product.product'].sudo().search([('id', '=', product_id)])
                for line in lines:
                    product_subtotal = product_subtotal + line.product_uom_qty
                    price_total = price_total + line.price_subtotal
                    price_total_withtax = price_total + (price_total * 0.15)
                if product_id in product_ids:
                    list2.append({
                        'product_code': product.default_code or '',
                        'product_name': product.name,
                        'product_qty': product_subtotal,
                        'invoice_value': price_total_withtax
                    })
                total_qty += product_subtotal
                total_invoice_value += price_total_withtax

        else:
            for line in sale_orders.mapped('order_line'):
                key = (line.product_id.id)
                product_wise_lines.setdefault(key, [])
                product_wise_lines[key].append(line)
            for product_id, lines in product_wise_lines.items():
                price_total = 0
                product_subtotal = 0
                price_total_withtax = 0
                product = self.env['product.product'].sudo().search([('id', '=', product_id)])
                for line in lines:
                    product_subtotal = product_subtotal + line.product_uom_qty
                    price_total = price_total + line.price_subtotal
                    price_total_withtax = price_total + (price_total * 0.15)
                list2.append({
                    'product_code': product.default_code or '',
                    'product_name': product.name,
                    'product_qty': product_subtotal,
                    'invoice_value': price_total_withtax
                })
                total_qty += product_subtotal
                total_invoice_value += price_total_withtax



        if sort_type == 'desc':
            return {
                'docs': docs,
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),
                'lines': sorted(list2, key=lambda l: l['invoice_value'],reverse= True),
                'total_qty': round(total_qty, 2),
                'total_invoice_value': total_invoice_value,
                'customer_type': type_list.get(olila_type) or '',
                'customer_name': self.env['res.partner'].browse(data.get('partner_id')).name or '',
                'zones': zones

            }
        elif sort_type == 'asc':
            return {
                'docs': docs,
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),
                'lines': sorted(list2, key=lambda l: l['invoice_value']),
                'total_qty': round(total_qty, 2),
                'total_invoice_value': total_invoice_value,
                'customer_type': type_list.get(olila_type) or '',
                'customer_name': self.env['res.partner'].browse(data.get('partner_id')).name or '',
                'zones': zones

            }
        else:
            return {
                'docs': docs,
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),
                'lines': list2,
                'total_qty': round(total_qty, 2),
                'total_invoice_value': total_invoice_value,
                'customer_type': type_list.get(olila_type) or '',
                'customer_name': self.env['res.partner'].browse(data.get('partner_id')).name or '',
                'zones': zones

            }