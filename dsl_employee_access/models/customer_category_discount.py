from datetime import datetime
from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

""" ===========Code Statements========
 **product_category 
 
 **discount_percentage
 
"""


class AppConfig(models.Model):
    _name = 'customer.category.discount'

    note = fields.Char(string='Discount Note')
    product_category = fields.Many2one('product.category', string='Product Category', required=True)
    discount_percentage = fields.Float(string='Discount %', default=0.0)
    partner_id = fields.Many2one('res.partner', string='Customer')

    _sql_constraints = [
        ('unique_product_category_partner_discount',
         'UNIQUE(product_category, partner_id)',
         'A duplicate product category for the same partner is not allowed!')
    ]


