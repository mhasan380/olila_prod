# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils
from datetime import datetime, timedelta

class StockClosingReportWizard(models.TransientModel):
    _name = 'stock.closing.report.wizard'

    product_id = fields.Many2one('product.product', 'Product')
    start_date = fields.Date("Start Date",
                             help="Select Start date which is mandatory \
                                     field for period range")
    end_date = fields.Date("End Date",
                           help="Select end date which is mandatory field \
                                   for period range")
    product_category = fields.Many2one('product.category',
                                            string="Product Category")
    warehouse_id = fields.Many2one('stock.warehouse', string='Depot')



    def get_report(self):
        today = fields.Date.today()
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'product_id': self.product_id.id,
                'start_date' : self.start_date,
                'end_date' : self.end_date,
                'product_category' : self.product_category.id,
                'warehouse_id' : self.warehouse_id.id,
                'location_id': self.warehouse_id.lot_stock_id.id,
            },
        }
        return self.env.ref('stock_balance_report.stock_closing_report').report_action(self, data=data)




class StockClosingReport(models.AbstractModel):

    _name = 'report.stock_balance_report.stock_closing_report_template'


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        product_id = data['form']['product_id']
        start_date = data['form']['start_date']
        end_date = data['form']['end_date']
        product_category = data['form']['product_category']
        warehouse_id = data['form']['warehouse_id']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)
        location_id = data['form']['location_id']
        category_name = self.env['product.category'].browse(product_category)


        stock_balance_dict = []

        if product_id:
            product_ids = self.env['product.product'].search([('id', '=', product_id)])
        else:
            product_ids = self.env['product.product'].search([('categ_id', '=', product_category),('type','=','product')])

        date_time = datetime.combine(datetime.strptime(start_date,"%Y-%m-%d"), datetime.min.time())
        end_time = datetime.combine(datetime.strptime(end_date,"%Y-%m-%d"), datetime.max.time())

        for product in product_ids:
            open_qty = product.with_context({'to_date': date_time,'location': location_id }).qty_available
            out_moves = self.env['stock.move'].search([('product_id', '=', product.id),
            ('date', '>=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
            ('date', '<=', end_time.strftime("%Y-%m-%d %H:%M:%S")), ('location_id', '=', location_id),('state','=','done')])
            out_qty = 0
            for move in out_moves:
                out_qty = out_qty + move.product_uom_qty
            in_moves = self.env['stock.move'].search([('product_id', '=', product.id),
                                                       ('date', '>=', date_time.strftime("%Y-%m-%d %H:%M:%S")),
                                                       ('date', '<=', end_time.strftime("%Y-%m-%d %H:%M:%S")),
                                                      ('location_dest_id', '=', location_id), ('state', '=', 'done')])
            in_qty = 0
            for rec in in_moves:
                in_qty = in_qty + rec.product_uom_qty
            current_qty = open_qty + in_qty - out_qty
            stock_balance_dict.append({'code': product.default_code,
                                                    'name': product.name,
                                                    'open_qty': open_qty,
                                                    'out_qty': out_qty,
                                                    'in_qty': in_qty,
                                                    'current_qty': current_qty,
                                                    'uom': product.uom_id.name
                                                    })



        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'stock_balance_dict': sorted(stock_balance_dict, key=lambda l: l['code']),
            'warehouse_name' : warehouse_name,
            'start_date' : start_date,
             'end_date': end_date,
            'category_name' : category_name

            }

