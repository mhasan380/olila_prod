# -*- coding: utf-8 -*-
# from odoo import http


# class PurchaseExtend(http.Controller):
#     @http.route('/purchase_extend/purchase_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/purchase_extend/purchase_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('purchase_extend.listing', {
#             'root': '/purchase_extend/purchase_extend',
#             'objects': http.request.env['purchase_extend.purchase_extend'].search([]),
#         })

#     @http.route('/purchase_extend/purchase_extend/objects/<model("purchase_extend.purchase_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('purchase_extend.object', {
#             'object': obj
#         })
