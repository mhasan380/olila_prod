# -*- coding: utf-8 -*-
# from odoo import http


# class ProductionModuleReports(http.Controller):
#     @http.route('/production_module_reports/production_module_reports/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/production_module_reports/production_module_reports/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('production_module_reports.listing', {
#             'root': '/production_module_reports/production_module_reports',
#             'objects': http.request.env['production_module_reports.production_module_reports'].search([]),
#         })

#     @http.route('/production_module_reports/production_module_reports/objects/<model("production_module_reports.production_module_reports"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('production_module_reports.object', {
#             'object': obj
#         })
