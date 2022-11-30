# -*- coding: utf-8 -*-
# from odoo import http


# class RoutePlanExtended(http.Controller):
#     @http.route('/route_plan_extended/route_plan_extended/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/route_plan_extended/route_plan_extended/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('route_plan_extended.listing', {
#             'root': '/route_plan_extended/route_plan_extended',
#             'objects': http.request.env['route_plan_extended.route_plan_extended'].search([]),
#         })

#     @http.route('/route_plan_extended/route_plan_extended/objects/<model("route_plan_extended.route_plan_extended"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('route_plan_extended.object', {
#             'object': obj
#         })
