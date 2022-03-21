# -*- coding: utf-8 -*-
# from odoo import http


# class LcLoanControlExtend(http.Controller):
#     @http.route('/lc_loan_control_extend/lc_loan_control_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lc_loan_control_extend/lc_loan_control_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lc_loan_control_extend.listing', {
#             'root': '/lc_loan_control_extend/lc_loan_control_extend',
#             'objects': http.request.env['lc_loan_control_extend.lc_loan_control_extend'].search([]),
#         })

#     @http.route('/lc_loan_control_extend/lc_loan_control_extend/objects/<model("lc_loan_control_extend.lc_loan_control_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lc_loan_control_extend.object', {
#             'object': obj
#         })
