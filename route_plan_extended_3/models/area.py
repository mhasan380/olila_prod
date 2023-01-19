from odoo import api, fields, models, _

class RouteArea(models.Model):
    _inherit = 'route.area'

    def assign_routes(self):
        self.customer_line_ids = [(6, 0, [])]
        filb_values = []
        route_list = self.env['route.master'].search([('area_id', '=', self.id)])
        for route in route_list:
            prod = (0, 0, {'route_id': route.id,
                           'route_code': route.route_id,
                           'coverage_area': route.coverage,
                           })
            filb_values.append(prod)
        self.write({'customer_line_ids': filb_values})



