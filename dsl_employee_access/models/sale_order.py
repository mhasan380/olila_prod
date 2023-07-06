from datetime import datetime
from odoo import models, fields, api
import logging
import hashlib
import os

_logger = logging.getLogger(__name__)

""" ===========Code Statements========
Author Md. Rafiul Hassan
"""


class SaleOrderInherit(models.Model):
    _inherit = 'sale.order'
    create_latitude = fields.Char(string='Create Latitude')
    create_longitude = fields.Char(string='Create Longitude')
    create_location_url = fields.Char(string='Create Location Url', compute='_compute_create_location_url_for_map')

    @api.depends('create_latitude', 'create_longitude')
    def _compute_create_location_url_for_map(self):
        for record in self:
            link_builder = f'https://www.google.com/maps/place/{record.create_latitude}+{record.create_longitude}/@{record.create_latitude},{record.create_longitude},17z'
            if record.create_latitude and record.create_longitude:
                record.create_location_url = link_builder
            else:
                record.create_location_url = ''

    def open_so_create_location(self):
        if self.id:
            return {
                'type': 'ir.actions.act_url',
                'url': self.create_location_url,
                'target': 'new',
            }
