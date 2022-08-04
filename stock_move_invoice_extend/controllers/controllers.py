# -*- coding: utf-8 -*-
# from odoo import http


# class StockMoveInvoiceExtend(http.Controller):
#     @http.route('/stock_move_invoice_extend/stock_move_invoice_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/stock_move_invoice_extend/stock_move_invoice_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('stock_move_invoice_extend.listing', {
#             'root': '/stock_move_invoice_extend/stock_move_invoice_extend',
#             'objects': http.request.env['stock_move_invoice_extend.stock_move_invoice_extend'].search([]),
#         })

#     @http.route('/stock_move_invoice_extend/stock_move_invoice_extend/objects/<model("stock_move_invoice_extend.stock_move_invoice_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('stock_move_invoice_extend.object', {
#             'object': obj
#         })
