# -*- coding: utf-8 -*-
# from odoo import http


# class InterTransReport(http.Controller):
#     @http.route('/inter_trans_report/inter_trans_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/inter_trans_report/inter_trans_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('inter_trans_report.listing', {
#             'root': '/inter_trans_report/inter_trans_report',
#             'objects': http.request.env['inter_trans_report.inter_trans_report'].search([]),
#         })

#     @http.route('/inter_trans_report/inter_trans_report/objects/<model("inter_trans_report.inter_trans_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('inter_trans_report.object', {
#             'object': obj
#         })
