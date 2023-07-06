# -*- coding: utf-8 -*-
# from odoo import http


# class AtnSummaryExtend(http.Controller):
#     @http.route('/atn_summary_extend/atn_summary_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/atn_summary_extend/atn_summary_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('atn_summary_extend.listing', {
#             'root': '/atn_summary_extend/atn_summary_extend',
#             'objects': http.request.env['atn_summary_extend.atn_summary_extend'].search([]),
#         })

#     @http.route('/atn_summary_extend/atn_summary_extend/objects/<model("atn_summary_extend.atn_summary_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('atn_summary_extend.object', {
#             'object': obj
#         })
