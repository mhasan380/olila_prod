# -*- coding: utf-8 -*-
# from odoo import http


# class RoutePlanExtended3(http.Controller):
#     @http.route('/route_plan_extended_3/route_plan_extended_3/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/route_plan_extended_3/route_plan_extended_3/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('route_plan_extended_3.listing', {
#             'root': '/route_plan_extended_3/route_plan_extended_3',
#             'objects': http.request.env['route_plan_extended_3.route_plan_extended_3'].search([]),
#         })

#     @http.route('/route_plan_extended_3/route_plan_extended_3/objects/<model("route_plan_extended_3.route_plan_extended_3"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('route_plan_extended_3.object', {
#             'object': obj
#         })
