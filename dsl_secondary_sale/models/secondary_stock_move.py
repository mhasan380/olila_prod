from datetime import datetime
from odoo import models, fields, api
import logging
import json

# Author - Md. Rafiul Hassan
# Daffodil Computers Ltd
# 12-09-2022

_logger = logging.getLogger(__name__)


class StockMoveSecondary(models.Model):
    _name = 'stock.move.secondary'
    secondary_sale_id = fields.Many2one('sale.secondary', string='Secondary Sale')
    secondary_stock_id = fields.Many2one('primary.customer.stocks', string='Secondary Stock', required=True)
    product_id = fields.Many2one('product.product', string='Products')
    quantity = fields.Float('Move Quantity')
    type = fields.Selection([('in', 'Stock In'), ('out', 'Stock Out')], required=True)
    secondary_customer_id = fields.Many2one('customer.secondary', string='Secondary Customer')
    multi_ref_id = fields.Many2one('stock.move.secondary.multi')
    is_adjustment = fields.Boolean("Adjustment", default=False)

    product_id_domain = fields.Char(
        compute="_compute_product_id_domain",
        readonly=True,
        store=False,
    )

    @api.depends('secondary_stock_id')
    def _compute_product_id_domain(self):
        product_list = []
        for rec in self:
            for stock_line in rec.secondary_stock_id.customer_stocks:
                product_list.append(stock_line.product_id.id)

            rec.product_id_domain = json.dumps(
                [('id', 'in', product_list)]
            )

    @api.model
    def create(self, vals):
        print(f'------------{vals}')
        if hasattr(vals, 'secondary_sale_id') and vals['secondary_sale_id']:
            vals['is_adjustment'] = False
        else:
            vals['is_adjustment'] = True
        record = super(StockMoveSecondary, self).create(vals)
        # if vals['type'] == 'in' and vals['secondary_stock_id']:
        #     print('------------'+str(['secondary_stock_id']))
        #     stock_id = self.env['primary.customer.stocks'].browse(vals['secondary_stock_id'])
        record.secondary_stock_id.action_sync_stock()
        return record
