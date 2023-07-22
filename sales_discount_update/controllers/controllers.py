# -*- coding: utf-8 -*-
# from odoo import http


# class SalesDiscountUpdate(http.Controller):
#     @http.route('/sales_discount_update/sales_discount_update/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sales_discount_update/sales_discount_update/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sales_discount_update.listing', {
#             'root': '/sales_discount_update/sales_discount_update',
#             'objects': http.request.env['sales_discount_update.sales_discount_update'].search([]),
#         })

#     @http.route('/sales_discount_update/sales_discount_update/objects/<model("sales_discount_update.sales_discount_update"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sales_discount_update.object', {
#             'object': obj
#         })
