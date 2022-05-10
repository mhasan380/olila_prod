# -*- coding: utf-8 -*-
# from odoo import http


# class VehiclePaperUpdateStatusReport(http.Controller):
#     @http.route('/transport_reports_olila/transport_reports_olila/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/transport_reports_olila/transport_reports_olila/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('transport_reports_olila.listing', {
#             'root': '/transport_reports_olila/transport_reports_olila',
#             'objects': http.request.env['transport_reports_olila.transport_reports_olila'].search([]),
#         })

#     @http.route('/transport_reports_olila/transport_reports_olila/objects/<model("transport_reports_olila.transport_reports_olila"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('transport_reports_olila.object', {
#             'object': obj
#         })
