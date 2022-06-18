# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils
from datetime import datetime, timedelta

class DeliveryPerformanceReportWizard(models.TransientModel):
    _name = 'delivered.performance.wizard'

    date_start = fields.Date(string="Start Date", required=True)
    date_end = fields.Date(string="End Date", required=True)
    warehouse_id = fields.Many2one('stock.warehouse', 'Depot')
    partner_id = fields.Many2one('res.partner', string='Customer')
    sale_type = fields.Selection([('primary_sales', 'Primary Sales'), ('corporate_sales', 'Corporate Sales'), ('all', 'All Sales')],default='primary_sales')
    sort_type = fields.Selection([('asc', 'Ascending'), ('desc', 'Descending')], string='Sort Type')


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
                'partner_id' : self.partner_id.id,
                'sort_type' : self.sort_type


                },
            }
        return self.env.ref('distribution_reports_olila.delivery_performance_report').report_action(self, data=data)




class DeliveredPerformanceReport(models.AbstractModel):

    _name = 'report.distribution_reports_olila.delivery_performance_template'


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        warehouse_id = data['form']['warehouse_id']
        location_id = data['form']['location_id']
        date_start = data['form']['date_start']
        date_end = data['form']['date_end']
        sale_type = data['form']['sale_type']
        sort_type = data['form']['sort_type']
        partner_id = data['form']['partner_id']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)

        from_date = datetime.combine(datetime.strptime(date_start,"%Y-%m-%d"), datetime.min.time())
        to_date = datetime.combine(datetime.strptime(date_end,"%Y-%m-%d"), datetime.max.time())


        depot_stock_dict =[]
        if location_id:
            depots = self.env['stock.warehouse'].search([('lot_stock_id', '=', location_id)])
        else:
            depots = self.env['stock.warehouse'].search([('is_depot', '=', True)])

        for depot in depots:
            if sale_type != 'all':
                delivery_orders = self.env['stock.picking'].search(
                [('location_id', '=', depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'), ('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                 ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")), ('sale_type', '=', sale_type), ('state', '=', 'done'),('transfer_id', '=', False)])
            else:
                delivery_orders = self.env['stock.picking'].search(
                            [('location_id', '=', depot.lot_stock_id.id), ('picking_type_code', '=', 'outgoing'),('scheduled_date', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                             ('scheduled_date', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S")), ('state', '=', 'done'),('sale_type', 'in', ('primary_sales','corporate_sales'))])
            for delivery in delivery_orders:
                total_product_delivery = sum(delivery.mapped('move_ids_without_package').mapped('quantity_done'))
                delivery_datetime = delivery.scheduled_date.date()
                if delivery.do_date:
                    so_date = delivery.do_date.date()
                else:
                    so_date = delivery.date_deadline.date()
                delivery_days = (delivery_datetime - so_date).days

                # depot_stock_dict.setdefault(delivery, {
                #     'customer_name': delivery.partner_id.name,
                #     'customer_code': delivery.partner_id.code,
                #     'address': delivery.partner_id.street,
                #     'do_date': delivery.scheduled_date.date(),
                #     'so_number': delivery.origin,
                #     'challan_number': delivery.name,
                #     'total_qty': total_product_delivery,
                #     'so_date': so_date,
                #     'delivery_days': delivery_days
                # })
                depot_stock_dict.append({
                    'customer_name': delivery.partner_id.name,
                    'customer_code': delivery.partner_id.code,
                    'address': delivery.partner_id.street,
                    'do_date': delivery.scheduled_date.date(),
                    'so_number': delivery.origin,
                    'challan_number': delivery.name,
                    'total_qty': total_product_delivery,
                    'so_date': so_date,
                    'delivery_days': delivery_days
                })

        if sort_type == 'desc':
            return {
                'doc_ids': data.get('docs'),
                'doc_model': data.get('model'),
                'warehouse_dict': sorted(depot_stock_dict, key=lambda l: l['delivery_days'], reverse= True),
                'date_start': date_start,
                'date_end': date_end,
                'warehouse_name': warehouse_name.name,
                'sale_type': sale_type
            }
        elif sort_type == 'asc':
            return {
                'doc_ids': data.get('docs'),
                'doc_model': data.get('model'),
                'warehouse_dict': sorted(depot_stock_dict, key=lambda l: l['delivery_days']),
                'date_start': date_start,
                'date_end': date_end,
                'warehouse_name': warehouse_name.name,
                'sale_type': sale_type
            }
        else:
            return {
                'doc_ids': data.get('docs'),
                'doc_model': data.get('model'),
                'warehouse_dict': depot_stock_dict,
                'date_start': date_start,
                'date_end': date_end,
                'warehouse_name': warehouse_name.name,
                'sale_type': sale_type
            }





