from datetime import datetime
from odoo import _, models, fields, api
import logging
from odoo.exceptions import UserError, ValidationError

# Author - Md. Rafiul Hassan
# Daffodil Computers Ltd
# 27-09-2022

_logger = logging.getLogger(__name__)


class PrimaryCustomerStocks(models.Model):
    _name = 'primary.customer.stocks'
    _sql_constraints = [
        ('customer_id_unique', 'unique(customer_id)', 'Stocks for the selected customer already exists!')
    ]
    name = fields.Char('Name', index=True, copy=False, default="New")
    customer_id = fields.Many2one('res.partner', string='Distributor', required=True, index=True,
                                  domain="[('is_customer', '=', True),('responsible', '!=', False)]")
    customer_street = fields.Char('Address', related='customer_id.street')
    customer_city = fields.Char('', related='customer_id.city')
    customer_country = fields.Many2one('res.country', string='', related='customer_id.country_id')
    customer_stocks = fields.One2many(comodel_name='product.line.secondary', inverse_name='primary_customer_stock_id',
                                      string='Stock Products')
    channel_commission = fields.Float(string='Channel Commission (%)', default=0.0)
    write_date = fields.Datetime('Last Updated on', index=True, readonly=True)

    enable_secondary_sale = fields.Boolean("Secondary Sale Enabled", default=True)

    total_stocks = fields.Float(string='Total Stock', compute='_compute_total_stock')

    def _compute_total_stock(self):
        for record in self:
            inc_sum = 0.0
            for stock_line in record.customer_stocks:
                inc_sum += stock_line.current_stock
            record.total_stocks = inc_sum

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            val['name'] = self.env['ir.sequence'].next_by_code('primary.customer.stocks') or '/'
        return super(PrimaryCustomerStocks, self).create(vals_list)

    def name_get(self):
        result = []
        for record in self:
            name = record.name
            if record.customer_id:
                name = '{} [{}]'.format(name, record.customer_id.name)
            result.append((record.id, name))
        return result

    def action_sync_stock(self):
        self.action_empty_stock()
        for rec in self:
            if rec.customer_id:
                pickings = self.env['stock.picking'].search([('partner_id', '=', rec.customer_id.id)])

                for picking in pickings:
                    if picking.picking_type_id.code == 'outgoing' and picking.state == 'done':
                        for stock_move in picking.move_lines:
                            self.update_product_stock_increase(stock_move.product_id, stock_move.quantity_done)

                    if picking.picking_type_id.code == 'incoming' and picking.state == 'done':
                        for stock_move in picking.move_lines:
                            self.update_product_stock_decrease(stock_move.product_id, stock_move.quantity_done)

            self.update_product_stock_after_secondary_sale()

    def update_product_stock_after_secondary_sale(self):
        secondary_stock_moves = self.env['stock.move.secondary'].search([('secondary_stock_id', '=', self.id)])
        if secondary_stock_moves:
            for move in secondary_stock_moves:
                secondary_product = self.env['product.line.secondary'].search(
                    [("product_id", "=", move.product_id.id), ("primary_customer_stock_id", '=', self.id)])
                if secondary_product:
                    if move.type == 'in':
                        new_stock = secondary_product.current_stock + move.quantity
                        secondary_product.write({'current_stock': new_stock})
                    elif move.type == 'out':
                        new_stock = secondary_product.current_stock - move.quantity
                        secondary_product.write({'current_stock': new_stock})
                else:
                    secondary_product = self.env['product.line.secondary'].create(
                        {
                            "product_id": move.product_id.id,
                            "primary_customer_stock_id": self.id,
                            "current_stock": move.quantity,
                            "sale_price": 0.0,
                        }
                    )

    def update_product_stock_increase(self, product_id, quantity_done):
        secondary_product = self.env['product.line.secondary'].search(
            [("product_id", "=", product_id.id), ("primary_customer_stock_id", '=', self.id)])
        if secondary_product:
            new_stock = secondary_product.current_stock + quantity_done
            secondary_product.write({'current_stock': new_stock})
        else:
            secondary_product = self.env['product.line.secondary'].create(
                {
                    "product_id": product_id.id,
                    "primary_customer_stock_id": self.id,
                    "current_stock": quantity_done,
                    "sale_price": 0.0,
                }
            )
        # self.update_product_stock_after_secondary_sale(product_id, secondary_product)

    def update_product_stock_decrease(self, product_id, quantity_done):
        secondary_product = self.env['product.line.secondary'].search(
            [("product_id", "=", product_id.id), ("primary_customer_stock_id", '=', self.id)])
        if secondary_product:
            new_stock = secondary_product.current_stock - quantity_done
            secondary_product.write({'current_stock': new_stock})
        else:
            secondary_product = self.env['product.line.secondary'].create(
                {
                    "product_id": product_id.id,
                    "primary_customer_stock_id": self.id,
                    "current_stock": quantity_done,
                    "sale_price": 0.0,
                }
            )
        # self.update_product_stock_after_secondary_sale(product_id, secondary_product)

    # def update_product_stock_after_secondary_sale(self, product_id, secondary_product):
    #
    #     secondary_stock_moves = self.env['stock.move.secondary'].search(
    #         [('secondary_stock_id', '=', self.id), ('product_id', '=', product_id.id)])
    #     if secondary_stock_moves:
    #         print(f'-------------------------111111--- {len(secondary_stock_moves)}')
    #         for move in secondary_stock_moves:
    #             if move.type == 'in':
    #                 new_stock = secondary_product.current_stock + move.quantity
    #                 secondary_product.write({'current_stock': new_stock})
    #             elif move.type == 'out':
    #                 new_stock = secondary_product.current_stock - move.quantity
    #                 secondary_product.write({'current_stock': new_stock})

    def action_clear_stock(self):
        for rec in self:
            rec.customer_stocks.unlink()

    def action_empty_stock(self):
        for rec in self:
            for line in rec.customer_stocks:
                line.current_stock = 0.0

    def preview_stock_adjustments(self):
        for rec in self:
            if len(rec.customer_stocks) > 0:
                return {
                    # 'name': self.order_id,
                    'res_model': 'stock.move.secondary.multi',
                    'type': 'ir.actions.act_window',
                    'context': {'default_secondary_stock_id': rec.id, 'form_view_initial_mode': 'edit',
                                'force_detailed_view': 'true'},
                    'view_mode': 'form',
                    'view_id': self.env.ref("dsl_secondary_sale.view_stock_adjustment_dialog_form").id,
                    'target': 'new'
                }
            else:
                raise ValidationError(_('No product found for adjustment.'))


class StockPickingInherited(models.Model):
    _inherit = 'stock.picking'

    def button_validate(self):
        return_value = super(StockPickingInherited, self).button_validate()
        if self.state == 'done' and self.partner_id:
            secondary_stock_id = self.env['primary.customer.stocks'].search([('customer_id', '=', self.partner_id.id)])
            if secondary_stock_id:
                for move_line in self.move_lines:
                    # if any(move_line.product_id == stock_line.product_id for stock_line in secondary_stock_id.customer_stocks):
                    #     self.update_product_stock_secondary(secondary_stock_id, stock_line, move_line)
                    # else:
                    #     self.create_product_stock_secondary(secondary_stock_id)
                    product_found = False
                    for stock_line in secondary_stock_id.customer_stocks:
                        if stock_line.product_id == move_line.product_id:
                            s_line = stock_line
                            product_found = True
                            break
                    if product_found:
                        self.update_product_stock_secondary(secondary_stock_id, s_line, move_line)
                    else:
                        self.create_product_stock_secondary(secondary_stock_id)

        return return_value

    def update_product_stock_secondary(self, secondary_stock_id, stock_line, move_line):
        if move_line.picking_type_id.code == 'outgoing':
            new_stock = stock_line.current_stock + move_line.quantity_done
            stock_line.write({'current_stock': new_stock})
        elif move_line.picking_type_id.code == 'incoming':
            new_stock = stock_line.current_stock - move_line.quantity_done
            stock_line.write({'current_stock': new_stock})

    def create_product_stock_secondary(self, secondary_stock_id):
        secondary_stock_id.action_sync_stock()

    # move_state_changed = fields.Char(compute="_compute_move_state_changed")

    # def write(self, vals):
    #     print('----------------change  ')
    #     print(vals)
    #     if  vals['state'] == 'done':
    #         print(vals)
    #         rec = self.env['stock.move'].browse(self._origin.id)
    #         if rec:
    #             picking_id = self.env['stock.picking'].browse(rec.picking_id.id)
    #             print(f'+++++++  {picking_id.id}')
    #
    #     # picking_id = self.env['stock.picking'].browse(vals['picking_id'])
    #     # secondary_stock = self.env['primary.customer.stocks'].search(
    #     #     [('customer_id', '=', picking_id.partner_id.id)])
    #     # print(f'========={secondary_stock.customer_id.name}')
    #     # if secondary_stock:
    #     #     self.env['product.line.secondary'].search([('product_id','=',self.product_id.id)])
    #     return super(StockMoveInherited, self).write(vals)

    # def button_validate(self):
    #
    #     process_done = super(StockMoveInherited, self).button_validate()
    #     if process_done:
    #         print(f'-----111   {self.id}')
    #     else:
    #         print(f'-----222   {self.id}')
    #     return process_done
