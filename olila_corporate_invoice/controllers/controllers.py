# -*- coding: utf-8 -*-
# from odoo import http


# class OlilaCorporateInvoice(http.Controller):
#     @http.route('/olila_corporate_invoice/olila_corporate_invoice/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/olila_corporate_invoice/olila_corporate_invoice/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('olila_corporate_invoice.listing', {
#             'root': '/olila_corporate_invoice/olila_corporate_invoice',
#             'objects': http.request.env['olila_corporate_invoice.olila_corporate_invoice'].search([]),
#         })

#     @http.route('/olila_corporate_invoice/olila_corporate_invoice/objects/<model("olila_corporate_invoice.olila_corporate_invoice"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('olila_corporate_invoice.object', {
#             'object': obj
#         })
