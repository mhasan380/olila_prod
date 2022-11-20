# -*- coding: utf-8 -*-
# from odoo import http


# class InternalTransferSummaryReport(http.Controller):
#     @http.route('/internal_transfer_summary_report/internal_transfer_summary_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/internal_transfer_summary_report/internal_transfer_summary_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('internal_transfer_summary_report.listing', {
#             'root': '/internal_transfer_summary_report/internal_transfer_summary_report',
#             'objects': http.request.env['internal_transfer_summary_report.internal_transfer_summary_report'].search([]),
#         })

#     @http.route('/internal_transfer_summary_report/internal_transfer_summary_report/objects/<model("internal_transfer_summary_report.internal_transfer_summary_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('internal_transfer_summary_report.object', {
#             'object': obj
#         })
