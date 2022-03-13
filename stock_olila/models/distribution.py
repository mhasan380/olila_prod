# -*- coding: utf-8 -*-

from odoo import api, fields, models

class VehicleDistribution(models.Model):
    _inherit = 'vehicle.distribution'


    def send_for_approval(self):
        self.state = 'approval'

        for delivery in self.delivery_ids:
            if self.transport_type == 'own':
                delivery.vehicle_no = self.vehicle_id.license_plate
            elif self.transport_type == 'rent':
                delivery.vehicle_no = self.rent_vehicle_nbr
                delivery.transporter_name = self.transport_company.name

            delivery.driver_name = self.driver_id.name
            delivery.driver_mobile = self.driver_contact
            delivery.vehicle_type = self.transport_type

    delivery_ids = fields.Many2many('stock.picking',
                                    domain="[('picking_type_code','in',('outgoing','internal')), ('state','=','done')]")



class Picking(models.Model):
    _inherit = 'stock.picking'

    vehicle_no = fields.Char(string="Vehicle No")
    vehicle_type = fields.Selection([('own', 'Own'), ('rent', '3rd Party/Rent')], string="Vehicle Type")
    driver_mobile = fields.Char(string="Driver Mobile No")

