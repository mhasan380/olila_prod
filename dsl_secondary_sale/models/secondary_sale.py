from datetime import datetime
from odoo import _, models, fields, api
import logging
from odoo.exceptions import UserError, ValidationError

# Author - Md. Rafiul Hassan
# Daffodil Computers Ltd
# 26-09-2022

_logger = logging.getLogger(__name__)


class SaleSecondary(models.Model):
    _name = 'sale.secondary'

    name = fields.Char('Name', index=True, copy=False, default="New")
    primary_customer_id = fields.Many2one('res.partner', string='Distributor', required=True, index=True,
                                          domain="[('is_customer', '=', True),('responsible', '!=', False)]")
    distributor_mobile = fields.Char('Contact', related='primary_customer_id.mobile')
    distributor_address = fields.Char('Address', related='primary_customer_id.street')
    responsible_id = fields.Many2one('hr.employee', string='Responsible', related='primary_customer_id.responsible')
    secondary_customer_id = fields.Many2one('customer.secondary', string='Secondary Customer', required=True,
                                            domain="[('partner_id', '=', primary_customer_id)]")
    secondary_customer_address = fields.Char(string='Address', related='secondary_customer_id.address')
    secondary_customer_mobile = fields.Char(string='Mobile', related='secondary_customer_id.mobile')
    sale_line_ids = fields.One2many(comodel_name='sale.secondary.line', inverse_name='secondary_sale_id',
                                    string='Products')
    latitude = fields.Char('Lat', copy=False)
    longitude = fields.Char('Long', copy=False)
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
        # ('cancelled', 'Cancelled'),
    ], default='draft')
    price_total = fields.Float(string='Subtotal', compute='_compute_price_total', store=True)
    company_id = fields.Many2one('res.company')

    @api.depends('sale_line_ids')
    def _compute_price_total(self):
        for rec in self:
            t_price = 0.0
            for sale_line in rec.sale_line_ids:
                t_price += sale_line.sub_total
            rec.price_total = t_price

    # btn_css = fields.Html(string='CSS', sanitize=False, compute='_compute_css', store=False)
    #
    # @api.depends('state')
    # def _compute_css(self):
    #
    #     for record in self:
    #         record.btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
    #         print(f'----------------{record.state}')
    #         # You can modify the below below condition
    #         if record.state != 'draft':
    #             record.btn_css = '<style>.o_form_button_edit {display: none !important;}</style>'
    #         else:
    #             record.btn_css = False

    def action_confirm_secondary_sale(self):
        for rec in self:
            if rec.state == 'confirmed':
                rec.state = 'draft'
            else:
                rec.state = 'confirmed'
                self.update_stock_move()

    def action_return_products(self):
        for rec in self:
            if rec.state == 'confirmed':
                return {
                    # 'name': self.order_id,
                    'res_model': 'stock.move.secondary.multi',
                    'type': 'ir.actions.act_window',
                    'context': {'default_secondary_sale_id': rec.id, 'form_view_initial_mode': 'edit',
                                'force_detailed_view': 'true'},
                    'view_mode': 'form',
                    'view_id': self.env.ref("dsl_secondary_sale.view_stock_return_dialog_form").id,
                    'target': 'current'
                }
            else:
                raise ValidationError(_('The order is not in Confirmed state.'))

    def update_stock_move(self):
        for rec in self:
            for sale_line in rec.sale_line_ids:
                stock_line = rec.env['product.line.secondary'].search(
                    [('primary_customer_stock_id', '=', sale_line.stock_id.id),
                     ('product_id', '=', sale_line.product_id.id)])
                if stock_line:
                    new_quantity = stock_line.current_stock - sale_line.quantity
                    stock_line.write({'current_stock': new_quantity})

                vals = {
                    'secondary_sale_id': rec.id,
                    'secondary_stock_id': sale_line.stock_id.id,
                    'product_id': sale_line.product_id.id,
                    'quantity': sale_line.quantity,
                    'type': 'out',
                    'secondary_customer_id': rec.secondary_customer_id.id
                }
                rec.env['stock.move.secondary'].create(vals)

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            val['name'] = self.env['ir.sequence'].next_by_code('sale.secondary') or '/'
        return super(SaleSecondary, self).create(vals_list)

    @api.onchange('primary_customer_id')
    def _onchange_primary_customer_id(self):
        self.secondary_customer_id = False
        self.secondary_customer_address = False
        self.secondary_customer_mobile = False
        self.sale_line_ids = False

    def unlink(self):
        for record in self:
            self.for_test_multi_move_delete(record)
            if record.state != "draft":
                raise ValidationError(_('The order is not in Draft state.'))
            children = self.mapped('sale_line_ids')
            if children:
                children.unlink()
            return super(SaleSecondary, self).unlink()

    def for_test_multi_move_delete(self, record):
        return_lines = self.env['stock.move.secondary.multi'].search([('secondary_sale_id', '=', record.id)])
        return_lines.unlink()

    def preview_move_lines(self):
        print('------------------')
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Move Lines',
            'view_mode': 'tree',
            'res_model': 'stock.move.secondary',
            'domain': [('secondary_sale_id', '=', self.id)],
            'context': "{'create': False}"
        }
