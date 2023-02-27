# -*- coding: utf-8 -*-
# from odoo import http


# class DailyProjection(http.Controller):
#     @http.route('/daily_projection/daily_projection/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/daily_projection/daily_projection/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('daily_projection.listing', {
#             'root': '/daily_projection/daily_projection',
#             'objects': http.request.env['daily_projection.daily_projection'].search([]),
#         })

#     @http.route('/daily_projection/daily_projection/objects/<model("daily_projection.daily_projection"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('daily_projection.object', {
#             'object': obj
#         })
