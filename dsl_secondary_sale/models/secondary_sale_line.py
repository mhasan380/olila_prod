from datetime import datetime
from odoo import models, fields, api
import logging
import json

# Author - Md. Rafiul Hassan
# Daffodil Computers Ltd
# 26-09-2022

_logger = logging.getLogger(__name__)


class SaleLineSecondary(models.Model):
    _name = 'sale.secondary.line'

    # name = fields.Char('Name', index=True, copy=False, default="New")
    # responsible_id = fields.Many2one('hr.employee', string='Responsible', related='primary_customer_id.responsible')
    # secondary_customer_id = fields.Many2one('customer.secondary', string='Secondary Customer', required=True,
    #                                         domain="[('partner_id', '=', primary_customer_id)]")
    secondary_sale_id = fields.Many2one('sale.secondary', string='Secondary Sale', required=True)
    primary_customer_id = fields.Many2one('res.partner', string='Seller/Primary Customer',
                                          related='secondary_sale_id.primary_customer_id')
    # This is Primary Customer Stocks
    stock_id = fields.Many2one('primary.customer.stocks', string='Secondary Stock')

    product_id_domain = fields.Char(
        compute="_compute_product_id_domain",
        readonly=True,
        store=False,
    )

    product_id = fields.Many2one('product.product', string='Products')  # domain="[('id', 'in', product_ids)]")
    quantity = fields.Float('Sale Quantity')
    sale_price_unit = fields.Float('Sale Price')
    sub_total = fields.Float(string='Subtotal', compute='_compute_subtotal', store=True)
    actual_total = fields.Float(string='Subtotal', compute='_compute_actual_total', store=True)
    company_id = fields.Many2one('res.company')
    sale_type = fields.Selection([
        ('master', 'Master'),
        ('inner', 'Inner')
    ])
    channel_commission_percentage = fields.Float('Commission %', default=0.0)
    channel_commission_amount = fields.Float('Commission Amount', compute='_compute_channel_commission_amount', store=True)

    @api.depends('channel_commission_percentage', 'quantity')
    def _compute_channel_commission_amount(self):
        for rec in self:
            if rec.channel_commission_percentage > 0.0 and rec.quantity > 0.0:
                _actual_price = rec.sale_price_unit * rec.quantity
                rec.channel_commission_amount = _actual_price * (rec.channel_commission_percentage / 100)
            else:
                rec.channel_commission_amount = 0.0

    @api.depends('quantity', 'sale_price_unit', 'channel_commission_amount')
    def _compute_subtotal(self):
        for rec in self:
            rec.sub_total = (rec.sale_price_unit * rec.quantity) - rec.channel_commission_amount

    @api.depends('quantity', 'sale_price_unit')
    def _compute_actual_total(self):
        for rec in self:
            rec.actual_total = rec.sale_price_unit * rec.quantity

    @api.depends('stock_id')
    def _compute_product_id_domain(self):
        product_list = []
        for rec in self:
            for stock_line in rec.stock_id.customer_stocks:
                product_list.append(stock_line.product_id.id)

            # rec.product_id_domain = {'domain': {'product_id': [('id', 'in', product_list)]}}

            rec.product_id_domain = json.dumps(
                [('id', 'in', product_list)]
            )

    # @api.model_create_multi
    # def create(self, vals_list):
    #     for val in vals_list:
    #         val['name'] = self.env['ir.sequence'].next_by_code('sale.secondary') or '/'
    #     return super(SaleSecondary, self).create(vals_list)
    #
    @api.onchange('product_id')
    def _onchange_primary_customer_id(self):

        for rec in self:
            dis_stok = rec.env['primary.customer.stocks'].search(
                [('customer_id', '=', rec.primary_customer_id.id)])

            rec.stock_id = dis_stok

            if rec.product_id:
                stock_line_id = rec.env['product.line.secondary'].search(
                    [('primary_customer_stock_id', '=', rec.stock_id.id), ('product_id', '=', rec.product_id.id)])
                print(f'ssssssssssssssssssssss   {stock_line_id.sale_price}')
                rec.sale_price_unit = stock_line_id.sale_price

            # for stock_line in dis_stok.customer_stocks:
            #     product_list.append(stock_line.product_id.id)
            #
            # rec.product_id_domain = {'domain': {'product_id': [('id', 'in', product_list)]}}
        # print(f'-----------------------exx  {self.primary_customer_id.name}')

    # @api.onchange('secondary_sale_id')
    # def _onchange_secondary_sale_id(self):
    #     print(f'------*************** {self.stock_id.name}')
    #
    # def _get_product_line_secondary(self):
    #     product_list = []
    #     print('------------------------------------ss')
    #     for rec in self:
    #         dis_stok =  rec.env['primary.customer.stocks'].search(
    #             [('customer_id', '=', rec.primary_customer_id.id)])
    #         rec.stock_id = dis_stok
    #
    #         for stock_line in dis_stok.customer_stocks:
    #             product_list.append(stock_line.product_id.id)
    #
    #         rec.product_id_domain = {'domain': {'product_id': [('id', 'in', product_list)]}}

    # for line in self:
    #     products = []
    #     for product_line in line.secondary_stock_id.customer_stocks:
    #         products.append(product_line.product_id)
    #     line.product_ids = products
