# -*- coding: utf-8 -*-
from odoo import fields, models, api


class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    sale_discount = fields.Float(string="Discount", config_parameter="3rd_party_depot.sale_discount")


