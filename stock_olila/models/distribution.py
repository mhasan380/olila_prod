# -*- coding: utf-8 -*-

from odoo import api, fields, models

class VehicleDistribution(models.Model):
    _inherit = 'vehicle.distribution'

    delivery_ids = fields.Many2many('stock.picking',
                                    domain="[('picking_type_code','in',('outgoing','internal')), ('state','=','done')]")

