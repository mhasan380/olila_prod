# -*- coding: utf-8 -*-
# from odoo import http


# class LcOpeningExtend(http.Controller):
#     @http.route('/lc_opening_extend/lc_opening_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lc_opening_extend/lc_opening_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lc_opening_extend.listing', {
#             'root': '/lc_opening_extend/lc_opening_extend',
#             'objects': http.request.env['lc_opening_extend.lc_opening_extend'].search([]),
#         })

#     @http.route('/lc_opening_extend/lc_opening_extend/objects/<model("lc_opening_extend.lc_opening_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lc_opening_extend.object', {
#             'object': obj
#         })
