# -*- coding: utf-8 -*-
# from odoo import http


# class OpeningUndXls(http.Controller):
#     @http.route('/opening_und_xls/opening_und_xls/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/opening_und_xls/opening_und_xls/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('opening_und_xls.listing', {
#             'root': '/opening_und_xls/opening_und_xls',
#             'objects': http.request.env['opening_und_xls.opening_und_xls'].search([]),
#         })

#     @http.route('/opening_und_xls/opening_und_xls/objects/<model("opening_und_xls.opening_und_xls"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('opening_und_xls.object', {
#             'object': obj
#         })
