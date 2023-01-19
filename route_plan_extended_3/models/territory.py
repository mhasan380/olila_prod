from odoo import api, fields, models, _

class RouteTerritory(models.Model):
    _inherit = 'route.territory'

    def assign_areas(self):
        areas = []
        area_list = self.env['route.area'].search([('territory_id', '=', self.id)])
        for area in area_list:
            if area.id not in areas:
                areas.append(area.id)
        self.update({
            'area_ids': [(6, 0, areas)],
        })



