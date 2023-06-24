from odoo import models, fields, api

""" ===========Code Statements========
Author Md. Rafiul Hassan
"""


class ProductCategoryInherit(models.Model):
    _inherit = 'product.category'
    discount_percentage = fields.Float('Discount %', default=0.0)
