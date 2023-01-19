# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class Partner(models.Model):
    _inherit = 'res.partner'

    division_id = fields.Many2one('route.division', string="Division")
    district_id = fields.Many2one('route.district', string="Distict")
    upazila_id = fields.Many2one('route.upazila', string="Upazila")
    union_id = fields.Many2one('route.union', string="Union")