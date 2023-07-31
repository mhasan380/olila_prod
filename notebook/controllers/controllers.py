# -*- coding: utf-8 -*-
# from odoo import http


# class Notebook(http.Controller):
#     @http.route('/notebook/notebook/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/notebook/notebook/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('notebook.listing', {
#             'root': '/notebook/notebook',
#             'objects': http.request.env['notebook.notebook'].search([]),
#         })

#     @http.route('/notebook/notebook/objects/<model("notebook.notebook"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('notebook.object', {
#             'object': obj
#         })
