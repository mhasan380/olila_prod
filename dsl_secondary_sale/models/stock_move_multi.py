from datetime import datetime
from odoo import models, fields, api, _
import logging
import json

# Author - Md. Rafiul Hassan
# Daffodil Computers Ltd
# 12-09-2022

_logger = logging.getLogger(__name__)


class StockMoveMulti(models.Model):
    _name = 'stock.move.secondary.multi'
    secondary_sale_id = fields.Many2one('sale.secondary', string='Secondary Sale')
    secondary_stock_id = fields.Many2one('primary.customer.stocks', string='Secondary Stock')
    move_ids = fields.One2many('stock.move.secondary', inverse_name='multi_ref_id', string='Movable Items',
                               required=True)

    @api.onchange('secondary_stock_id')
    def _onchange_secondary_stock_id(self):
        for rec in self:
            if not rec.secondary_sale_id:
                print('--------------ccsss')

    @api.onchange('secondary_sale_id')
    def _onchange_secondary_sale_id(self):
        print('--------------------------------------------- on change')
        # related_lines = self.move_ids.browse([])
        # for sale_line in self.secondary_sale_id.sale_line_ids:
        #     stock_id = self.env['primary.customer.stocks'].search(
        #         [('customer_id', '=', self.secondary_sale_id.primary_customer_id.id)])
        #     related_lines += related_lines.new({
        #         'secondary_sale_id': self.secondary_sale_id.id,
        #         'secondary_stock_id': stock_id.id,
        #         'product_id': sale_line.product_id.id,
        #         'quantity': 0.0,
        #         'type': 'in',
        #         'secondary_customer_id': self.secondary_sale_id.secondary_customer_id.id
        #     })
        # self.move_ids = related_lines
        # print('-------wwww' + str(len(self.move_ids)))

        for rec in self:
            if rec.secondary_sale_id:
                rec.move_ids = [(5, 0, 0)]
                lines = [(5, 0, 0)]
                sale_lines = rec.secondary_sale_id.sale_line_ids
                if sale_lines:
                    for sale_line in sale_lines:
                        stock_id = self.env['primary.customer.stocks'].search(
                            [('customer_id', '=', rec.secondary_sale_id.primary_customer_id.id)])
                        move_line = {
                            'secondary_sale_id': rec.secondary_sale_id.id,
                            'secondary_stock_id': stock_id.id,
                            'product_id': sale_line.product_id.id,
                            'quantity': 0.0,
                            'type': 'in',
                            'secondary_customer_id': rec.secondary_sale_id.secondary_customer_id.id
                        }
                        lines.append((0, 0, move_line))
                rec.move_ids = lines

    @api.model
    def create(self, vals):
        res = super(StockMoveMulti, self).create(vals)
        return res
