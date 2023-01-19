# -*- coding: utf-8 -*-
# from odoo import http


# class RoutePlanExtended4(http.Controller):
#     @http.route('/route_plan_extended_4/route_plan_extended_4/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/route_plan_extended_4/route_plan_extended_4/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('route_plan_extended_4.listing', {
#             'root': '/route_plan_extended_4/route_plan_extended_4',
#             'objects': http.request.env['route_plan_extended_4.route_plan_extended_4'].search([]),
#         })

#     @http.route('/route_plan_extended_4/route_plan_extended_4/objects/<model("route_plan_extended_4.route_plan_extended_4"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('route_plan_extended_4.object', {
#             'object': obj
#         })
