# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils

class CurrentStockReportWizard(models.TransientModel):
    _name = 'current.stock.report.wizard'

    warehouse_id = fields.Many2one('stock.warehouse', 'Stock Location')
    product_category = fields.Many2one('product.category', string="Category")


    def get_report(self):
        today = fields.Date.today()
        warehouse_id = self.warehouse_id
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'warehouse_id':warehouse_id.id,
                'location_id' : warehouse_id.lot_stock_id.id,
                'product_category':self.product_category.id,
            },
        }
        return self.env.ref('stock_details_report_oilia.current_stock_report').report_action(self, data=data)




class CurrentStockReport(models.AbstractModel):

    _name = 'report.stock_details_report_oilia.current_stock_report_template'

    def percentage(self, part, whole):
        if whole: 
            return "{:.1%}".format(float(part)/float(whole))
        return 0


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        warehouse_id = data['form']['warehouse_id']
        location_id = data['form']['location_id']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)
        product_category = data['form']['product_category']
        domain=[('location_id', '=', location_id)]
        if product_category:
            domain.append(('product_id.categ_id', '=', product_category))
        quants = self.env['stock.quant'].search(domain)



        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'quants': quants,
            'warehouse_name' : warehouse_name
            }

