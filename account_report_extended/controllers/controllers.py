# -*- coding: utf-8 -*-
# from odoo import http


# class AccountReportExtended(http.Controller):
#     @http.route('/account_report_extended/account_report_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/account_report_extended/account_report_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('account_report_extended.listing', {
#             'root': '/account_report_extended/account_report_extended',
#             'objects': http.request.env['account_report_extended.account_report_extended'].search([]),
#         })

#     @http.route('/account_report_extended/account_report_extended/objects/<model("account_report_extended.account_report_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('account_report_extended.object', {
#             'object': obj
#         })
