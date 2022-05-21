from odoo import models, fields, api

class FleetVehicleLogContract(models.Model):
    _inherit = 'fleet.vehicle.log.contract'

    def open_license_renewals(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Licence Renewals',
            'view_mode': 'tree,form',
            'res_model': 'vehicle.liecense.renew',
            'domain': [('licence_id', '=', self.id)],
            'context': {'default_vehicle_id': self.vehicle_id.id}
        }


class LicenseRenewal(models.Model):
    _inherit = 'vehicle.liecense.renew'

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")