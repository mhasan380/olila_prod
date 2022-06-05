# -*- coding: utf-8 -*-
from datetime import datetime
from odoo import api, fields, models,_


class VehicleDistribution(models.Model):
    _inherit = 'vehicle.distribution'

    depot_id = fields.Many2one()