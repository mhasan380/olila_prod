# -*- coding: utf-8 -*-
# from odoo import http


# class StockBalanceReport(http.Controller):
#     @http.route('/stock_balance_report/stock_balance_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_balance_report/stock_balance_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_balance_report.listing', {
#             'root': '/stock_balance_report/stock_balance_report',
#             'objects': http.request.env['stock_balance_report.stock_balance_report'].search([]),
#         })

#     @http.route('/stock_balance_report/stock_balance_report/objects/<model("stock_balance_report.stock_balance_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_balance_report.object', {
#             'object': obj
#         })
