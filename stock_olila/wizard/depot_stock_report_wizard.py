# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils

class DepotStockReportWizard(models.TransientModel):
    _name = 'depot.stock.report.wizard'

    warehouse_id = fields.Many2one('stock.warehouse', 'Depot')


    def get_report(self):
        today = fields.Date.today()
        warehouse_id = self.warehouse_id
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'warehouse_id':warehouse_id.id,
            },
        }
        return self.env.ref('stock_olila.depot_stock_report').report_action(self, data=data)




class DepotStockReport(models.AbstractModel):

    _name = 'report.stock_olila.depot_stock_report_template'

    def percentage(self, part, whole):
        if whole: 
            return "{:.1%}".format(float(part)/float(whole))
        return 0


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        warehouse_id = data['form']['warehouse_id']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)

        depot_stock_dict = {}
        depots = self.env['stock.warehouse'].search([('is_depot', '=', True )])
        for depot in depots:
            delivery_orders = self.env['stock.picking'].search([('location_id', '=', depot.lot_stock_id.id),('picking_type_code', '=', 'outgoing'),('state', 'in',('confirmed','assigned'))])
            retail_undelivery = 0.0
            corprate_undelivry = 0.0
            for order in delivery_orders:
                if order.sale_type == 'primary_sales':
                    retail_undelivery += sum(order.mapped('move_ids_without_package').mapped('product_uom_qty'))
                elif order.sale_type == 'corporate_sales':
                    corprate_undelivry += sum(order.mapped('move_ids_without_package').mapped('product_uom_qty'))
            total_undelivery = retail_undelivery + corprate_undelivry
            quants = self.env['stock.quant'].search([('location_id', '=',depot.lot_stock_id.id)])
            total_stock = 0.0
            total_sale_price = 0.0
            for quant in quants:
                total_stock += quant.quantity
                total_sale_price += (quant.quantity * quant.product_id.lst_price)

            depot_stock_dict.setdefault(depot, {'depot_name': depot.name,
                                                     'total_stock': total_stock,
                                                     'retail_undelivery': retail_undelivery,
                                                      'corporate_undelivery': corprate_undelivry,
                                                      'total_undelivery': total_undelivery,
                                                      'retail_net_stock': total_stock - retail_undelivery,
                                                      'net_stock': total_stock - total_undelivery,
                                                      'total_sale_price': total_sale_price
                                                      })





        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'warehouse_dict': list(depot_stock_dict.values()),


            }

