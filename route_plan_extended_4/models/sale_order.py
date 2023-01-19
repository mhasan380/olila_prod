# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    division_id = fields.Many2one('route.division', string="Division", related='partner_id.division_id')
    district_id = fields.Many2one('route.district', string="Distict", related='partner_id.district_id')
    upazila_id = fields.Many2one('route.upazila', string="Upazila", related='partner_id.upazila_id')
    union_id = fields.Many2one('route.union', string="Union", related='partner_id.union_id')