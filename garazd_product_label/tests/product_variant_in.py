# -*- coding: utf-8 -*-

from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.product'
    page_number = fields.Char(string='Page Number')
