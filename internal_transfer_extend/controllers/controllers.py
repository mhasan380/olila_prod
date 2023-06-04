# -*- coding: utf-8 -*-
# from odoo import http


# class InternalTransferExtend(http.Controller):
#     @http.route('/internal_transfer_extend/internal_transfer_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/internal_transfer_extend/internal_transfer_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('internal_transfer_extend.listing', {
#             'root': '/internal_transfer_extend/internal_transfer_extend',
#             'objects': http.request.env['internal_transfer_extend.internal_transfer_extend'].search([]),
#         })

#     @http.route('/internal_transfer_extend/internal_transfer_extend/objects/<model("internal_transfer_extend.internal_transfer_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('internal_transfer_extend.object', {
#             'object': obj
#         })
