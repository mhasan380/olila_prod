# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils
from datetime import datetime, timedelta

class UndeliverValueReportWizard(models.TransientModel):
    _name = 'undeliverd.value.wizard'

    date = fields.Date('Date')
    sale_type = fields.Selection([('primary_sales', 'Primary Sales'), ('corporate_sales', 'Corporate Sales'),('all', 'All Sales')],
                                 default='primary_sales')
    warehouse_id = fields.Many2one('stock.warehouse', string='Depot')
    partner_id = fields.Many2one('res.partner', string='Customer')
    sort_type = fields.Selection([('asc','Smallest to Largest'),('desc','Largest to Smallest')])


    def get_report(self):
        today = fields.Date.today()
        warehouse_id = self.warehouse_id
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'warehouse_id':warehouse_id.id,
                'location_id' : warehouse_id.lot_stock_id.id,
                'date' : self.date,
                'sale_type' : self.sale_type,
                'partner_id': self.partner_id.id,
                'sort_type' : self.sort_type

            },
        }
        return self.env.ref('sale_report_extend.undelivery_value_report').report_action(self, data=data)




class UndeliveryValueReport(models.AbstractModel):

    _name = 'report.sale_report_extend.undelivery_value_template'


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        warehouse_id = data['form']['warehouse_id']
        location_id = data['form']['location_id']
        date = data['form']['date']
        sale_type = data['form']['sale_type']
        partner_id = data['form']['partner_id']
        sort_type = data['form']['sort_type']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)

        if date:
            date_time = datetime.combine(datetime.strptime(date,"%Y-%m-%d"), datetime.max.time())
        else:
            today = fields.Datetime.today()
            date_time = datetime.combine(today, datetime.max.time())

        delivery_orders = self.env['stock.picking'].search(
                [('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                 ('sale_type', 'in', ('primary_sales','corporate_sales')), ('transfer_id', '=', False), ('state', 'in', ('confirmed', 'assigned'))])
        if sale_type != 'all':
            delivery_orders = self.env['stock.picking'].search(
                [('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                 ('sale_type', '=', sale_type), ('transfer_id', '=', False), ('state', 'in', ('confirmed', 'assigned'))])
        else:
            delivery_orders = self.env['stock.picking'].search(
                [('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                 ('transfer_id', '=', False), ('state', 'in', ('confirmed', 'assigned'))])
        if partner_id:
            delivery_orders = self.env['stock.picking'].search(
                [('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                 ('transfer_id', '=', False), ('partner_id','=',partner_id), ('state', 'in', ('confirmed', 'assigned'))])

        if location_id:
            delivery_orders = self.env['stock.picking'].search(
                [('location_id', '=', location_id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                 ('transfer_id', '=', False), ('partner_id','=',partner_id), ('state', 'in', ('confirmed', 'assigned'))])

        lines = []
        customer_list = []
        for order in delivery_orders:
            if order.partner_id not in customer_list:
                customer_list.append(order.partner_id)
        for customer in customer_list:
            orders = []
            for record in delivery_orders:
                if record.partner_id == customer:
                    orders.append(record)
            total_pending = 0.0
            total_qty = 0.0
            for order in orders:
                pending_amount = 0.0
                quantity = 0.0
                for line in order.move_ids_without_package:
                   product_id = line.product_id.id
                   quantity += line.product_uom_qty
                   price_unit = line.sale_line_id.price_unit if line.sale_line_id else line.product_id.lst_price
                   discount = line.sale_line_id.discount
                   pending_amount += ((price_unit - (price_unit * discount) / 100) * line.product_uom_qty)
                total_pending += pending_amount
                total_qty += quantity
            lines.append({
                'code': customer.code,
                'name': customer.name,
                'qty': total_qty,
                'value' : total_pending

            })

        if sort_type == 'asc':
            return {
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),

                'warehouse_name' : warehouse_name,
                'sale_type': sale_type,
                'date': date,
                'lines': sorted(lines, key=lambda l: l['value']),

                }
        elif sort_type == 'desc':
            return {
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),

                'warehouse_name': warehouse_name,
                'sale_type': sale_type,
                'date': date,
                'lines': sorted(lines, key=lambda l: l['value'],reverse=True),

            }
        else:
            return {
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),

                'warehouse_name': warehouse_name,
                'sale_type': sale_type,
                'date': date,
                'lines': lines,

            }



