# -*- coding: utf-8 -*-
# from odoo import http


# class BankPaymentVoucher(http.Controller):
#     @http.route('/bank_payment_voucher/bank_payment_voucher/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/bank_payment_voucher/bank_payment_voucher/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('bank_payment_voucher.listing', {
#             'root': '/bank_payment_voucher/bank_payment_voucher',
#             'objects': http.request.env['bank_payment_voucher.bank_payment_voucher'].search([]),
#         })

#     @http.route('/bank_payment_voucher/bank_payment_voucher/objects/<model("bank_payment_voucher.bank_payment_voucher"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('bank_payment_voucher.object', {
#             'object': obj
#         })
