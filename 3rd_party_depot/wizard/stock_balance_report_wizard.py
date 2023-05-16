# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils
from datetime import datetime, timedelta

class DepotValueWizard(models.TransientModel):
    _name = 'depot.value.wizard'

    warehouse_id = fields.Many2one('stock.warehouse', string='Depot')
    product_category = fields.Many2one('product.category',
                                       string="Product Category")



    def get_report(self):
        today = fields.Date.today()
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'warehouse_id' : self.warehouse_id.id,
                'product_category': self.product_category.id,
                'location_id': self.warehouse_id.lot_stock_id.id,
            },
        }
        return self.env.ref('3rd_party_depot.depot_value_report').report_action(self, data=data)




class DepotValueReport(models.AbstractModel):

    _name = 'report.3rd_party_depot.depot_value_report_template'


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        product_category = data['form']['product_category']
        warehouse_id = data['form']['warehouse_id']
        location_id = data['form']['location_id']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)
        category_name = self.env['product.category'].browse(product_category)



        stock_balance_dict = []

        domain = [
            ('location_id', '=', location_id)
        ]

        if product_category:
            domain.append(('product_id.categ_id', '=', product_category))

        stock_moves = self.env['stock.quant'].search(domain)
        discount_percent = float(self.env['ir.config_parameter'].sudo().get_param('3rd_party_depot.sale_discount')) or 0
        total_value = 0
        total_stock = 0

        for move in stock_moves:
            sale_value = (move.quantity * move.product_id.lst_price)
            discount = (move.quantity * move.product_id.lst_price * (discount_percent / 100))
            if move.product_id.fs_type == 'master':
                stock_value = sale_value - discount
            else:
                stock_value = sale_value
            stock_balance_dict.append({'code': move.product_id.default_code,
                                                        'name': move.product_id.name,
                                                        'qty': move.quantity,
                                                        'value': stock_value,
                                                        'uom': move.product_id.uom_id.name
                                                        })
            total_value += stock_value
            total_stock += move.quantity


        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'stock_balance_dict': sorted(stock_balance_dict, key=lambda l: l['code']),
            'warehouse_name' : warehouse_name,
            'total_value' : total_value,
            'category_name': category_name,
            'total_stock' : total_stock
            }

