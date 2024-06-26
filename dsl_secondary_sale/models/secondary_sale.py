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
    create_responsible_id = fields.Many2one('hr.employee', string='Create Responsible')
    secondary_customer_id = fields.Many2one('customer.secondary', string='Secondary Customer', required=True,
                                            domain="[('partner_id', '=', primary_customer_id)]")
    secondary_customer_address = fields.Char(string='Address', related='secondary_customer_id.address')
    secondary_customer_mobile = fields.Char(string='Mobile', related='secondary_customer_id.mobile')
    sale_line_ids = fields.One2many(comodel_name='sale.secondary.line', inverse_name='secondary_sale_id',
                                    string='Products')
    latitude = fields.Char('Lat', copy=False)
    longitude = fields.Char('Long', copy=False)
    channel_commission = fields.Float(string='Channel Commission', compute='_compute_channel_commission', store=True)

    create_location_url = fields.Char(string='Create Location Url', compute='_compute_create_location_url_for_map')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirmed', 'Confirmed')
        # ('cancelled', 'Cancelled'),
    ], default='draft')
    price_total = fields.Float(string='Gross Amount', compute='_compute_price_total', store=True)
    total_commission = fields.Float(string='Commission', compute='_compute_total_commission', store=True)
    net_amount = fields.Float(string='Net Amount', compute='_compute_total_net_amount', store=True)
    company_id = fields.Many2one('res.company')

    #####All related fields
    division_id = fields.Many2one('route.division', string='Division', related='secondary_customer_id.division_id')
    district_id = fields.Many2one('route.district', string='District', related='secondary_customer_id.district_id')
    upazila_id = fields.Many2one('route.upazila', string='Upazila', related='secondary_customer_id.upazila_id')
    union_id = fields.Many2one('route.union', string='Union', related='secondary_customer_id.union_id')
    route_id = fields.Many2one('route.master', string='Route', related='secondary_customer_id.route_id')
    so_market_id = fields.Many2one('route.area', string='SO Market', related='secondary_customer_id.so_market_id')
    territory_id = fields.Many2one('route.territory', string='Territory', related='secondary_customer_id.territory_id')
    region_id = fields.Many2one('res.zone', string='Region', related='secondary_customer_id.region_id')

    # type = fields.Char(related='secondary_customer_id.type', string='Customer Type')

    @api.depends('sale_line_ids')
    def _compute_price_total(self):
        for rec in self:
            t_price = 0.0
            for sale_line in rec.sale_line_ids:
                t_price += sale_line.actual_total
            rec.price_total = t_price

    @api.depends('sale_line_ids')
    def _compute_total_commission(self):
        for rec in self:
            t_commission = 0.0
            for sale_line in rec.sale_line_ids:
                t_commission += sale_line.channel_commission_amount
            rec.total_commission = t_commission

    @api.depends('total_commission', 'price_total')
    def _compute_total_net_amount(self):
        for rec in self:
            rec.net_amount = rec.price_total - rec.total_commission

    @api.depends('primary_customer_id')
    def _compute_channel_commission(self):
        for rec in self:
            distributor_stock = rec.env['primary.customer.stocks'].search(
                [('customer_id', '=', rec.primary_customer_id.id)])
            if distributor_stock:
                rec.channel_commission = distributor_stock.channel_commission
            else:
                rec.channel_commission = 0.0

    @api.depends('latitude', 'longitude')
    def _compute_create_location_url_for_map(self):
        for record in self:
            link_builder = f'https://www.google.com/maps/place/{record.latitude}+{record.longitude}/@{record.latitude},{record.longitude},17z'
            if record.latitude and record.longitude:
                record.create_location_url = link_builder
            else:
                record.create_location_url = ''

    def open_so_create_location(self):
        if self.id:
            return {
                'type': 'ir.actions.act_url',
                'url': self.create_location_url,
                'target': 'new',
            }

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
