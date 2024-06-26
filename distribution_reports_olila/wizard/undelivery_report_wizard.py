# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils
from datetime import datetime, timedelta

class UndelideryReportWizard(models.TransientModel):
    _name = 'undeliverd.report.wizard'

    date = fields.Date('Date')
    report_type = fields.Selection([('depot','Depot Wise'),('product','Product Wise'),('customer','Customer Wise')])
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
                'report_type' : self.report_type,
                'sale_type' : self.sale_type,
                'partner_id': self.partner_id.id,
                'sort_type' : self.sort_type

            },
        }
        return self.env.ref('distribution_reports_olila.undelivery_stock_report').report_action(self, data=data)




class UndeliveryStockReport(models.AbstractModel):

    _name = 'report.distribution_reports_olila.undelivery_report_template'


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        warehouse_id = data['form']['warehouse_id']
        location_id = data['form']['location_id']
        date = data['form']['date']
        report_type = data['form']['report_type']
        sale_type = data['form']['sale_type']
        partner_id = data['form']['partner_id']
        sort_type = data['form']['sort_type']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)

        if date:
            date_time = datetime.combine(datetime.strptime(date,"%Y-%m-%d"), datetime.max.time())
        else:
            today = fields.Datetime.today()
            date_time = datetime.combine(today, datetime.max.time())

        depot_stock_dict = {}
        if report_type == 'depot':
            if sale_type != 'all':
                delivery_orders = self.env['stock.picking'].search(
                [('location_id', '=', location_id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                 ('sale_type', '=', sale_type), ('transfer_id', '=', False), ('state', 'in', ('confirmed', 'assigned'))])
            else:
                delivery_orders = self.env['stock.picking'].search(
                    [('location_id', '=', location_id), ('picking_type_code', '=', 'outgoing'),('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                     ('transfer_id', '=', False), ('state', 'in', ('confirmed', 'assigned'))])
            for order in delivery_orders:
                for line in order.move_ids_without_package:
                    key = (line.product_id)
                    depot_stock_dict.setdefault(key, 0.0)
                    depot_stock_dict[key] += line.product_uom_qty

            if sort_type == 'desc':
                return {
                    'doc_ids': data.get('ids'),
                    'doc_model': data.get('model'),

                    'warehouse_name': warehouse_name,
                    'sale_type': sale_type,
                    'date': date,
                    'report_type': report_type,
                    'depot_stock_dict': sorted([{
                        'product_id': product.id,
                        'product_name': product.name,
                        'code': product.default_code,
                        'quantity': qty,
                        'uom': product.uom_id.name,
                        'fs_type': product.fs_type
                    } for (product), qty in depot_stock_dict.items()], key=lambda l: l['quantity'],reverse=True),
                }
            elif sort_type == 'asc':

                return {
                    'doc_ids': data.get('ids'),
                    'doc_model': data.get('model'),

                    'warehouse_name': warehouse_name,
                    'sale_type': sale_type,
                    'date': date,
                    'report_type': report_type,
                    'depot_stock_dict': sorted([{
                        'product_id': product.id,
                        'product_name': product.name,
                        'code': product.default_code,
                        'quantity': qty,
                        'uom': product.uom_id.name,
                        'fs_type': product.fs_type
                    } for (product), qty in depot_stock_dict.items()], key=lambda l: l['quantity']),
                  }

            else:
                return {
                    'doc_ids': data.get('ids'),
                    'doc_model': data.get('model'),

                    'warehouse_name': warehouse_name,
                    'sale_type': sale_type,
                    'date': date,
                    'report_type': report_type,
                    'depot_stock_dict': sorted([{
                        'product_id': product.id,
                        'product_name': product.name,
                        'code': product.default_code,
                        'quantity': qty,
                        'uom': product.uom_id.name,
                        'fs_type': product.fs_type
                    } for (product), qty in depot_stock_dict.items()], key=lambda l: l['code']),
                }


        elif report_type == 'product':
            depots = self.env['stock.warehouse'].search([('is_depot', '=', True)])
            for depot in depots:
                if sale_type != 'all':
                    delivery_orders = self.env['stock.picking'].search(
                        [('location_id', '=', depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                         ('sale_type', '=', sale_type), ('transfer_id', '=', False), ('state', 'in', ('confirmed', 'assigned'))])
                else:
                    delivery_orders = self.env['stock.picking'].search(
                        [('location_id', '=', depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                         ('transfer_id', '=', False),   ('state', 'in', ('confirmed', 'assigned'))])
                for order in delivery_orders:
                    for line in order.move_ids_without_package:
                        key = (line.product_id)
                        depot_stock_dict.setdefault(key, 0.0)
                        depot_stock_dict[key] += line.product_uom_qty

            if sort_type == 'desc':
                return {
                    'doc_ids': data.get('ids'),
                    'doc_model': data.get('model'),

                    'warehouse_name': warehouse_name,
                    'sale_type': sale_type,
                    'date': date,
                    'report_type': report_type,
                    'depot_stock_dict': sorted([{
                        'product_id': product.id,
                        'product_name': product.name,
                        'code': product.default_code,
                        'quantity': qty,
                        'uom': product.uom_id.name,
                        'fs_type': product.fs_type
                    } for (product), qty in depot_stock_dict.items()], key=lambda l: l['quantity'],reverse=True),
                }
            elif sort_type == 'asc':

                return {
                    'doc_ids': data.get('ids'),
                    'doc_model': data.get('model'),

                    'warehouse_name': warehouse_name,
                    'sale_type': sale_type,
                    'date': date,
                    'report_type': report_type,
                    'depot_stock_dict': sorted([{
                        'product_id': product.id,
                        'product_name': product.name,
                        'code': product.default_code,
                        'quantity': qty,
                        'uom': product.uom_id.name,
                        'fs_type': product.fs_type
                    } for (product), qty in depot_stock_dict.items()], key=lambda l: l['quantity']),
                  }

            else:
                return {
                    'doc_ids': data.get('ids'),
                    'doc_model': data.get('model'),

                    'warehouse_name': warehouse_name,
                    'sale_type': sale_type,
                    'date': date,
                    'report_type': report_type,
                    'depot_stock_dict': sorted([{
                        'product_id': product.id,
                        'product_name': product.name,
                        'code': product.default_code,
                        'quantity': qty,
                        'uom': product.uom_id.name,
                        'fs_type': product.fs_type
                    } for (product), qty in depot_stock_dict.items()], key=lambda l: l['code']),
                }

        elif report_type == 'customer':
            if warehouse_id:
                depots = self.env['stock.warehouse'].search([('is_depot', '=', True),('lot_stock_id', '=', location_id)])
            else:
                depots = self.env['stock.warehouse'].search([('is_depot', '=', True)])
            for depot in depots:
                if sale_type != 'all':
                    delivery_orders = self.env['stock.picking'].search(
                        [('location_id', '=', depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                         ('sale_type', '=', sale_type), ('transfer_id', '=', False), ('state', 'in', ('confirmed', 'assigned'))])
                else:
                    delivery_orders = self.env['stock.picking'].search(
                        [('location_id', '=', depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                         ('transfer_id', '=', False), ('state', 'in', ('confirmed', 'assigned'))])
                if partner_id:
                    delivery_orders = self.env['stock.picking'].search(
                        [('location_id', '=', depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '<=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                         ('transfer_id', '=', False), ('partner_id','=',partner_id), ('state', 'in', ('confirmed', 'assigned'))])

                for order in delivery_orders:
                    for line in order.move_ids_without_package:
                        key = (order.partner_id, line.product_id)
                        depot_stock_dict.setdefault(key, 0.0)
                        depot_stock_dict[key] += line.product_uom_qty


            return {
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),

                'warehouse_name' : warehouse_name,
                'sale_type': sale_type,
                'date': date,
                'report_type':report_type,
                'depot_stock_dict': sorted([{
                    'product_id': product.id,
                    'product_name': product.name,
                    'code': product.default_code,
                    'quantity': qty,
                    'uom': product.uom_id.name,
                    'customer_name':customer.display_name,
                    'customer_code' : customer.code,
                    'customer': customer,
                    'fs_type': product.fs_type
                } for (customer,product), qty in depot_stock_dict.items()], key=lambda l: l['customer_name']),
                }


