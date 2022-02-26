# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils

class RawStockReportWizard(models.TransientModel):
    _name = 'raw.stock.report.wizard'

    consumtion = fields.Float('Total Consumtion(Ton)')


    def get_report(self):
        today = fields.Date.today()
        consumtion = self.consumtion
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'consumtion':consumtion,
            },
        }
        return self.env.ref('stock_olila.raw_stock_report').report_action(self, data=data)




class RawStockReport(models.AbstractModel):

    _name = 'report.stock_olila.raw_stock_report_template'

    def percentage(self, part, whole):
        if whole: 
            return "{:.1%}".format(float(part)/float(whole))
        return 0


    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        consumtion = data['form']['consumtion']

        if consumtion:
            total_consumtion = consumtion * 1000
        else:
            total_consumtion = 33225.0

        stock_dict = {}
        products = self.env['product.product'].search([('categ_id', '=', 'Raw Materials'),('active','=', True)])
        for product in products:
            code = product.default_code
            quantity = self.env['stock.quant'].search([('location_id', '=', 'GENST/Stock'),('product_id', '=', product.id)],limit = 1).quantity
            if product.default_code == '3794':
                daily_consumtion = total_consumtion * 0.5485
            elif product.default_code == '3792':
                daily_consumtion = total_consumtion * 0.0361
            elif product.default_code == '3771':
                daily_consumtion = total_consumtion * 0.0185
            elif product.default_code == '3776':
                daily_consumtion = total_consumtion * 0.0271
            elif product.default_code == '3780':
                daily_consumtion = total_consumtion * 0.0169
            elif product.default_code == '3796':
                daily_consumtion = total_consumtion * 0.0045
            elif product.default_code == '3797':
                daily_consumtion = total_consumtion * 0.0339
            elif product.default_code == '3775':
                daily_consumtion = total_consumtion * 0.0102
            elif product.default_code == '3777':
                daily_consumtion = total_consumtion * 0.0903
            elif product.default_code == '3795':
                daily_consumtion = total_consumtion * 0.1625
            elif product.default_code == '3784':
                daily_consumtion = total_consumtion * 0.0361
            elif product.default_code == '3784':
                daily_consumtion = total_consumtion * 0.0361
            elif product.default_code == '3783':
                daily_consumtion = total_consumtion * 0.0181
            else:
                daily_consumtion = 0.0
            stock_days = 0.0
            if daily_consumtion != 0:
                stock_days = quantity / daily_consumtion

            stock_dict.setdefault(product, {'code': code,
                                                     'product_name': product.name,
                                                     'quantity': quantity,
                                                      'daily_consumtion': daily_consumtion,
                                                      'stock_days': stock_days,
                                                                                                          })





        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'stock_dict': list(stock_dict.values()),
         }

