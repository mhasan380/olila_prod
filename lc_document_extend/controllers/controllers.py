# -*- coding: utf-8 -*-
# from odoo import http


# class LcDocumentExtend(http.Controller):
#     @http.route('/lc_document_extend/lc_document_extend/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/lc_document_extend/lc_document_extend/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('lc_document_extend.listing', {
#             'root': '/lc_document_extend/lc_document_extend',
#             'objects': http.request.env['lc_document_extend.lc_document_extend'].search([]),
#         })

#     @http.route('/lc_document_extend/lc_document_extend/objects/<model("lc_document_extend.lc_document_extend"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('lc_document_extend.object', {
#             'object': obj
#         })
