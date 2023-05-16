# -*- coding: utf-8 -*-
# from odoo import http


# class 3rdPartyDepot(http.Controller):
#     @http.route('/3rd_party_depot/3rd_party_depot/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/3rd_party_depot/3rd_party_depot/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('3rd_party_depot.listing', {
#             'root': '/3rd_party_depot/3rd_party_depot',
#             'objects': http.request.env['3rd_party_depot.3rd_party_depot'].search([]),
#         })

#     @http.route('/3rd_party_depot/3rd_party_depot/objects/<model("3rd_party_depot.3rd_party_depot"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('3rd_party_depot.object', {
#             'object': obj
#         })
