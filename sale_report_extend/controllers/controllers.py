# -*- coding: utf-8 -*-
# from odoo import http


# class SaleReportExtend(http.Controller):
#     @http.route('/sale_report_extend/sale_report_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_report_extend/sale_report_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_report_extend.listing', {
#             'root': '/sale_report_extend/sale_report_extend',
#             'objects': http.request.env['sale_report_extend.sale_report_extend'].search([]),
#         })

#     @http.route('/sale_report_extend/sale_report_extend/objects/<model("sale_report_extend.sale_report_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_report_extend.object', {
#             'object': obj
#         })
