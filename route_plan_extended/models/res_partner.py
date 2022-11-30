# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class Partner(models.Model):
    _inherit = 'res.partner'

    area_id = fields.Many2one('route.area', string="Area")
    territory_id = fields.Many2one('route.territory', string="Territory")
    route_id = fields.Many2one('route.master', string="Route ID")
    division = fields.Selection([
        ('Dhaka', 'Dhaka'),
        ('Barisal', 'Barishal'),
        ('Chattogram', 'Chattogram'),
        ('Khulna', 'Khulna'),
        ('Rangpur', 'Rangpur'),
        ('Rajshahi', 'Rajshahi'),
        ('Mymensingh ', 'Mymensingh '),
        ('Sylhet ', 'Sylhet '),
    ], string='Division')