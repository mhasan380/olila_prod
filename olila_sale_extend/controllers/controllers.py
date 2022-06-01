# -*- coding: utf-8 -*-
# from odoo import http


# class OlilaSaleExtend(http.Controller):
#     @http.route('/olila_sale_extend/olila_sale_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/olila_sale_extend/olila_sale_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('olila_sale_extend.listing', {
#             'root': '/olila_sale_extend/olila_sale_extend',
#             'objects': http.request.env['olila_sale_extend.olila_sale_extend'].search([]),
#         })

#     @http.route('/olila_sale_extend/olila_sale_extend/objects/<model("olila_sale_extend.olila_sale_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('olila_sale_extend.object', {
#             'object': obj
#         })
