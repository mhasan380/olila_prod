from datetime import datetime
from odoo import models, fields, api
import logging

# Author - Md. Rafiul Hassan
# Daffodil Computers Ltd
# 27-09-2022

_logger = logging.getLogger(__name__)


class SecondaryProductLine(models.Model):
    _name = 'product.line.secondary'

    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_code = fields.Char('Code', related='product_id.default_code')
    primary_customer_stock_id = fields.Many2one('primary.customer.stocks', string='Customer Stock', required=True)
    current_stock = fields.Float('Stock (Units)')
    sale_price = fields.Float('Unit Price', compute="_compute_sales_price")
    enabled = fields.Boolean("Enabled", default=True)

    @api.depends('product_id')
    def _compute_sales_price(self):
        for product in self:
            if product.product_id:
                product.sale_price = product.product_id.lst_price
            else:
                product.sale_price = 0.0


