# -*- coding: utf-8 -*-
# from odoo import http


# class DistributionReportExtend(http.Controller):
#     @http.route('/distribution_report_extend/distribution_report_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/distribution_report_extend/distribution_report_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('distribution_report_extend.listing', {
#             'root': '/distribution_report_extend/distribution_report_extend',
#             'objects': http.request.env['distribution_report_extend.distribution_report_extend'].search([]),
#         })

#     @http.route('/distribution_report_extend/distribution_report_extend/objects/<model("distribution_report_extend.distribution_report_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('distribution_report_extend.object', {
#             'object': obj
#         })
