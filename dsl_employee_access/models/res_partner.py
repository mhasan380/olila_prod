from odoo import models, fields, api

""" ===========Code Statements========
Author Md. Rafiul Hassan
"""


class ProductCategoryInherit(models.Model):
    _inherit = 'res.partner'
    discount_line_ids = fields.One2many(comodel_name='customer.category.discount', inverse_name='partner_id',
                                    string='Discounts %')

    @api.constrains('discount_line_ids')
    def _check_duplicate_category_ids(self):
        for partner in self:
            category_ids = partner.discount_line_ids.mapped('product_category')
            if len(category_ids) != len(set(category_ids)):
                raise ValidationError('Duplicate product categories found in category discounts!')

