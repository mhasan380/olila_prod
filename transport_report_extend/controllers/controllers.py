# -*- coding: utf-8 -*-
# from odoo import http


# class TransportReportExtend(http.Controller):
#     @http.route('/transport_report_extend/transport_report_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/transport_report_extend/transport_report_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('transport_report_extend.listing', {
#             'root': '/transport_report_extend/transport_report_extend',
#             'objects': http.request.env['transport_report_extend.transport_report_extend'].search([]),
#         })

#     @http.route('/transport_report_extend/transport_report_extend/objects/<model("transport_report_extend.transport_report_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('transport_report_extend.object', {
#             'object': obj
#         })
