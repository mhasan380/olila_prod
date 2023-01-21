from odoo import api, fields, models
from datetime import date


class Planning(models.Model):
    _inherit = 'sales.person.plan'

    @api.onchange('route_type')
    def on_change_route_type(self):
        if self.route_type:
            return {'domain': {'route_ids': [('route_type', '=', self.route_type)]}}

    route_type = fields.Selection([
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('corporate', 'Corporate')
    ], string='Route Type')
    route_ids = fields.Many2many('route.master', string="Routes")
    route_code = fields.Char(string="Route ID")
    coverage = fields.Char(string="Coverage Area")
    deputy_ids = fields.Many2one('hr.employee', string="Deputy NSM")
    dsm_ids = fields.Many2one('hr.employee', string="DSM")
    zone_ids = fields.Many2many('res.zone', string="Region")
    territory_ids = fields.Many2many('route.territory', string="Territory")
    area_ids = fields.Many2many('route.area', string="Area")
    days_ids = fields.Many2many('route.day', string="Days")

    # @api.onchange('route_ids')
    # def on_change_route_ids(self):
    #     self.info_checklist = [(6, 0, [])]
    #     filb_values = []
    #     areas = []
    #     zones = []
    #     territories = []
    #     route_codes = ''
    #     cover = ''
    #     if self.route_ids:
    #         for route in self.route_ids:
    #             if route.route_type == "primary":
    #                 for line in route.primary_customer_ids:
    #                     prod = (0, 0, {'customer': line.customer_id.id,
    #                                    'status': 'todo',
    #                                    'name': self.name,
    #                                    })
    #                     filb_values.append(prod)
    #
    #             elif route.route_type == "corporate":
    #                 for line in route.corporate_customer_ids:
    #                     prod = (0, 0, {'customer': line.customer_id.id,
    #                                    'status': 'todo',
    #                                    'name': self.name,
    #                                    })
    #                     filb_values.append(prod)
    #             elif route.route_type == "secondary":
    #                 for line in route.secondary_customer_ids:
    #                     prod = (0, 0, {'secondary_customer': line.customer_id.id,
    #                                    'status': 'todo',
    #                                    })
    #                     filb_values.append(prod)
    #             route_codes += route.route_id + ','
    #             cover += route.coverage + ','
    #             if route.area_id.id not in areas:
    #                 areas.append(route.area_id.id)
    #             if route.zone_id.id not in zones:
    #                 zones.append(route.zone_id.id)
    #             if route.territory_id.id not in territories:
    #                 territories.append(route.territory_id.id)
    #
    #     self.update({'info_checklist': filb_values})
    #
    #     self.update({
    #         'area_ids': [(6, 0, areas)],
    #         'territory_ids': [(6, 0, territories)],
    #         'zone_ids': [(6, 0, zones)],
    #         'route_code': route_codes,
    #         'coverage': cover,
    #     })

# class CheckList(models.Model):
#     _inherit = 'rode.list'
#
#     secondary_customer = fields.Many2one('customer.secondary', string="Secondary Customer")
