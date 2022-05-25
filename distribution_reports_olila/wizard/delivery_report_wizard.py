# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils
from datetime import datetime, timedelta

class DeliverdReportWizard(models.TransientModel):
    _name = 'delivered.report.wizard'

    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    report_type = fields.Selection([('depot','Depot Wise'),('product','Product Wise'),('customer','Customer Wise'), ('national','National')])
    warehouse_id = fields.Many2one('stock.warehouse', 'Depot')
    partner_id = fields.Many2one('res.partner', string='Customer')
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
                'partner_id' : self.partner_id.id


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
        partner_id = data['form']['partner_id']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)

        from_date = datetime.combine(datetime.strptime(date_start,"%Y-%m-%d"), datetime.min.time())
        to_date = datetime.combine(datetime.strptime(date_end,"%Y-%m-%d"), datetime.max.time())

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

        elif report_type == 'national':
            depot_stock_dict = {}
            depots = self.env['stock.warehouse'].search([('is_depot', '=', True)])
            for depot in depots:
                deivery_orders = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'), ('location_id', '=', depot.lot_stock_id.id),
                                                                   ('transfer_id', '=', False)])
                opening_orders = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'), ('location_id', '=', depot.lot_stock_id.id),
                                            ('transfer_id', '=', False),('date_deadline', '<', from_date.strftime("%Y-%m-%d %H:%M:%S")),('state', 'in', ('confirmed', 'assigned'))])

                retail_undelivery = 0.0
                corprate_undelivry = 0.0
                primary_percent = 0.0
                corporate_percent = 0.0
                total_percent = 0.0
                for order in opening_orders:
                    if order.sale_type == 'primary_sales':
                        retail_undelivery += sum(order.mapped('move_ids_without_package').mapped('product_uom_qty'))
                    elif order.sale_type == 'corporate_sales':
                        corprate_undelivry += sum(order.mapped('move_ids_without_package').mapped('product_uom_qty'))
                total_undelivery = retail_undelivery + corprate_undelivry
                current_orders = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'), ('location_id', '=', depot.lot_stock_id.id),
                                            ('transfer_id', '=', False),('date_deadline', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")), ('date_deadline', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")), ('state', 'not in', ('draft', 'cancel'))])
                corporate_orders = current_orders.filtered(lambda x: x.sale_type and x.sale_type == 'corporate_sales')
                corporate_total_qty = sum(corporate_orders.mapped('move_ids_without_package').mapped('product_uom_qty'))
                corporate_deiverd_orders = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'), ('location_id', '=', depot.lot_stock_id.id),
                                            ('transfer_id', '=', False),('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                        ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")), ('state', '=', 'done'),('sale_type', '=', 'corporate_sales')])

                corporate_deiverd_qty = sum(corporate_deiverd_orders.mapped('move_ids_without_package').mapped('quantity_done'))
                primary_orders = current_orders.filtered(lambda x: x.sale_type and x.sale_type == 'primary_sales')
                primary_total_qty = sum(primary_orders.mapped('move_ids_without_package').mapped('product_uom_qty'))
                primary_deiverd_orders = self.env['stock.picking'].search([('picking_type_code', '=', 'outgoing'), ('location_id', '=', depot.lot_stock_id.id),
                                            ('transfer_id', '=', False),('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                        ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")), ('state', '=', 'done'),('sale_type', '=', 'primary_sales')])
                primary_deiverd_qty = sum(primary_deiverd_orders.mapped('move_ids_without_package').mapped('quantity_done'))
                if primary_total_qty > 0:
                    primary_percent = ((primary_deiverd_qty / primary_total_qty) * 100)
                if corporate_total_qty > 0:
                    corporate_percent = ((corporate_deiverd_qty / corporate_total_qty) * 100)
                total_qty = primary_total_qty + corporate_total_qty
                total_delivery = primary_deiverd_qty + corporate_deiverd_qty
                if total_qty > 0:
                    total_percent = (total_delivery / total_qty) * 100

                depot_stock_dict.setdefault(depot, {
                                                    'depot_name': depot.name,
                                                    'cor_opening_qty': corprate_undelivry,
                                                    'pri_opening_qty': retail_undelivery,
                                                    'corporate_total_qty': corporate_total_qty,
                                                    'primary_total_qty': primary_total_qty,
                                                    'corporate_deiverd_qty': corporate_deiverd_qty,
                                                     'primary_deiverd_qty': primary_deiverd_qty,
                                                     'primary_percent' : primary_percent,
                                                      'corporate_percent' : corporate_percent,
                                                       'total_percent' : total_percent

                                                            })

            return {
                'doc_ids': data.get('docs'),
                'doc_model': data.get('model'),
                'warehouse_dict': list(depot_stock_dict.values()),
                'report_type': report_type,
                'date_start': date_start,
                'date_end': date_end,


            }

        elif report_type == 'customer':
            depot_stock_dict = {}

            depot = self.env['stock.warehouse'].search([('is_depot', '=', True),('lot_stock_id', '=', location_id)])

            if sale_type != 'all':
                delivery_orders = self.env['stock.picking'].search(
                    [('location_id', '=', depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                     ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")),   ('sale_type', '=', sale_type), ('transfer_id', '=', False), ('state', '=', 'done')])
            else:
                delivery_orders = self.env['stock.picking'].search(
                    [('location_id', '=', depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                     ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")),
                     ('transfer_id', '=', False), ('state', '=', 'done')])
            if partner_id:
                delivery_orders = self.env['stock.picking'].search(
                    [('location_id', '=', depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                     ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")),
                     ('transfer_id', '=', False), ('partner_id','=',partner_id), ('state', '=', 'done')])

            for order in delivery_orders:
                for line in order.move_ids_without_package:
                    key = (order.partner_id, line.product_id)
                    depot_stock_dict.setdefault(key, 0.0)
                    depot_stock_dict[key] += line.quantity_done


            return {
                'doc_ids': data.get('ids'),
                'doc_model': data.get('model'),

                'warehouse_name' : warehouse_name,
                'sale_type': sale_type,
                'date_start': date_start,
                'date_end': date_end,
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


