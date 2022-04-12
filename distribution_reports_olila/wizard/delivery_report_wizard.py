# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils
from datetime import datetime, timedelta

class DeliverdReportWizard(models.TransientModel):
    _name = 'delivered.report.wizard'

    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    report_type = fields.Selection([('depot','Depot Wise'),('product','Product Wise'), ('national','National')])
    warehouse_id = fields.Many2one('stock.warehouse', 'Depot')
    sort_type = fields.Selection([('asc', 'Smallest to Largest'), ('desc', 'Largest to Smallest')])
    sale_type = fields.Selection([('primary_sales', 'Primary Sales'), ('corporate_sales', 'Corporate Sales'), ('all', 'All Sales')],default='primary_sales')


    def get_report(self):
        today = fields.Date.today()
        warehouse_id = self.warehouse_id
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'warehouse_id': warehouse_id.id,
                'location_id' : warehouse_id.lot_stock_id.id,
                'date_start' : self.date_start,
                'date_end' : self.date_end,
                'sale_type' : self.sale_type,
                'sort_type' : self.sort_type,
                'report_type' : self.report_type,


                },
            }
        return self.env.ref('distribution_reports_olila.delivered_stock_report').report_action(self, data=data)




class DeliveredStockReport(models.AbstractModel):

    _name = 'report.distribution_reports_olila.delivered_report_template'


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        warehouse_id = data['form']['warehouse_id']
        location_id = data['form']['location_id']
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        report_type = data['form']['report_type']
        sale_type = data['form']['sale_type']
        sort_type = data['form']['sort_type']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)

        from_date = datetime.combine(datetime.strptime(date_start,"%Y-%m-%d"), datetime.min.time())
        to_date = datetime.combine(datetime.strptime(date_end,"%Y-%m-%d"), datetime.min.time())

        if report_type == 'depot':
            depot_stock_dict ={}
            if sale_type != 'all':
                delivery_orders = self.env['stock.picking'].search(
                [('location_id', '=', location_id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                 ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")), ('sale_type', '=', sale_type), ('state', '=', 'done'),('transfer_id', '=', False)])
            else:
                delivery_orders = self.env['stock.picking'].search(
                            [('location_id', '=', location_id), ('picking_type_code', '=', 'outgoing'),('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                             ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")), ('state', '=', 'done'),('transfer_id', '=', False)])
            for delivery in delivery_orders:
                total_product_delivery = sum(delivery.mapped('move_ids_without_package').mapped('quantity_done'))

                depot_stock_dict.setdefault(delivery, {
                                                    'customer_name': delivery.partner_id.name,
                                                    'address': delivery.partner_id.street,
                                                    'date': delivery.scheduled_date.date(),
                                                    'so_number': delivery.origin,
                                                    'challan_number': delivery.name,
                                                    'total_qty': total_product_delivery,
                                                    })


            return {
                'doc_ids': data.get('docs'),
                'doc_model': data.get('model'),
                'warehouse_dict': list(depot_stock_dict.values()),
                'report_type': report_type,
                'date_start' : date_start,
                'date_end' : date_end,
                'warehouse_name' : warehouse_name.name,
                'sale_type' : sale_type
               }


        elif  report_type == 'product':
            depot_stock_dict = {}
            if location_id:
                depots = self.env['stock.warehouse'].search([('lot_stock_id', '=', location_id)])
            else:
                depots = self.env['stock.warehouse'].search([('is_depot', '=', True)])

            for depot in depots:
                if sale_type != 'all':
                    delivery_orders = self.env['stock.picking'].search(
                    [('location_id', '=',  depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                     ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")), ('sale_type', '=', sale_type), ('state', '=', 'done'),('transfer_id', '=', False)])
                else:
                    delivery_orders = self.env['stock.picking'].search(
                                [('location_id', '=',  depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'),('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                                 ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")), ('state', '=', 'done'),('transfer_id', '=', False)])
                for delivery in delivery_orders:
                    for line in delivery.move_ids_without_package:
                        key = (line.product_id)
                        depot_stock_dict.setdefault(key, 0.0)
                        depot_stock_dict[key] += line.quantity_done

            if sort_type == 'desc':
                return {
                    'doc_ids': data.get('ids'),
                    'doc_model': data.get('model'),
                    'date_start': date_start,
                    'date_end': date_end,
                    'warehouse_name': warehouse_name.name,
                    'sale_type': sale_type,
                    'report_type': report_type,
                    'depot_stock_dict': sorted([{
                        'product_id': product.id,
                        'product_name': product.name,
                        'code': product.default_code,
                        'quantity': qty,
                        'uom': product.uom_id.name
                    } for (product), qty in depot_stock_dict.items()], key=lambda l: l['quantity'],reverse=True),
                }
            elif sort_type == 'asc':

                return {
                    'doc_ids': data.get('ids'),
                    'doc_model': data.get('model'),

                    'warehouse_name': warehouse_name.name,
                    'sale_type': sale_type,
                    'date_start': date_start,
                    'date_end': date_end,
                    'report_type': report_type,
                    'depot_stock_dict': sorted([{
                        'product_id': product.id,
                        'product_name': product.name,
                        'code': product.default_code,
                        'quantity': qty,
                        'uom': product.uom_id.name
                    } for (product), qty in depot_stock_dict.items()], key=lambda l: l['quantity']),
                  }

            else:
                return {
                    'doc_ids': data.get('ids'),
                    'doc_model': data.get('model'),

                    'warehouse_name': warehouse_name.name,
                    'sale_type': sale_type,
                    'date_start': date_start,
                    'date_end': date_end,
                    'report_type': report_type,
                    'depot_stock_dict': sorted([{
                        'product_id': product.id,
                        'product_name': product.name,
                        'code': product.default_code,
                        'quantity': qty,
                        'uom': product.uom_id.name
                    } for (product), qty in depot_stock_dict.items()], key=lambda l: l['product_name']),
                }




