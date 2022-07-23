# -*- coding: utf-8 -*-
# from odoo import http


# class CustomerDetailsReport(http.Controller):
#     @http.route('/customer_details_report/customer_details_report/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/customer_details_report/customer_details_report/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('customer_details_report.listing', {
#             'root': '/customer_details_report/customer_details_report',
#             'objects': http.request.env['customer_details_report.customer_details_report'].search([]),
#         })

#     @http.route('/customer_details_report/customer_details_report/objects/<model("customer_details_report.customer_details_report"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('customer_details_report.object', {
#             'object': obj
#         })
