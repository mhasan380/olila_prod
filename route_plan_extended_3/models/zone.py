from odoo import api, fields, models, _

class Zone(models.Model):
    _inherit = 'res.zone'

    def assign_territory(self):
        territories = []
        territory_list = self.env['route.territory'].search([('zone_id', '=', self.id)])
        for terrytory in territory_list:
            if terrytory.id not in territories:
                territories.append(terrytory.id)
        self.update({
            'territory_ids': [(6, 0, territories)],
        })