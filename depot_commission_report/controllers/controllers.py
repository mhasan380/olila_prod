# -*- coding: utf-8 -*-
# from odoo import http


# class DepotCommissionReport(http.Controller):
#     @http.route('/depot_commission_report/depot_commission_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/depot_commission_report/depot_commission_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('depot_commission_report.listing', {
#             'root': '/depot_commission_report/depot_commission_report',
#             'objects': http.request.env['depot_commission_report.depot_commission_report'].search([]),
#         })

#     @http.route('/depot_commission_report/depot_commission_report/objects/<model("depot_commission_report.depot_commission_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('depot_commission_report.object', {
#             'object': obj
#         })
