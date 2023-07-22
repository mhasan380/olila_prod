# -*- coding: utf-8 -*-
from odoo import models, fields, api
from odoo.exceptions import ValidationError


class SaleDiscountUpdate(models.Model):
    _name = 'discount.update'
    _description = 'Sales Discount Update'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.onchange('region')
    def on_change_region(self):
        if self.region:
            return {'domain': {'territory': [('zone_id', '=', self.region.id)]}}

    @api.onchange('territory')
    def on_change_territory(self):
        if self.territory:
            return {'domain': {'area': [('territory_id', '=', self.territory.id)]}}

    @api.onchange('area')
    def on_change_area(self):
        if self.area:
            return {'domain': {'route': [('area_id', '=', self.area.id)]}}

    @api.onchange('division')
    def on_change_division(self):
        if self.division:
            return {'domain': {'district': [('division_id', '=', self.division.id)]}}

    @api.onchange('district')
    def on_change_district(self):
        if self.district:
            return {'domain': {'upazila': [('district_id', '=', self.district.id)]}}

    @api.onchange('upazila')
    def on_change_upazila(self):
        if self.upazila:
            return {'domain': {'union': [('upazila_id', '=', self.upazila.id)]}}

    name = fields.Char('Description')
    date = fields.Date('Date', tracking=True)
    region = fields.Many2one('res.zone', string='Region')
    territory = fields.Many2one('route.territory', string='Territory')
    area = fields.Many2one('route.area', string='Area')
    route = fields.Many2one('route.master', string='Route')
    division = fields.Many2one('route.division', string='Division')
    district = fields.Many2one('route.district', string='District')
    upazila = fields.Many2one('route.upazila', string='Upazila')
    union = fields.Many2one('route.union', string='Union')
    remarks = fields.Char('Remarks')
    state = fields.Selection(
        [('draft', 'Draft'), ('first', 'First Approval'), ('second', 'Second Approval'), ('final', 'Final Approval'),
         ('cancel', 'Cancel')],
        string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    discount_line_ids = fields.One2many(comodel_name='discount.update.line', inverse_name='discount_id',
                                        string='Discounts %')

    def first_approval(self):
        self.state = 'first'
    def second_approval(self):
        self.state = 'second'
    def button_draft(self):
        self.state = 'draft'
    def button_cancel(self):
        self.state = 'cancel'

    def final_approval(self):
        domain = [
            ('is_customer', '=', True),
            ("olila_type", "!=", 'corporater'),
        ]
        if self.region:
            domain.append(('zone_id', '=', self.region.id))
        if self.territory:
            domain.append(('territory_id', '=', self.territory.id))
        if self.area:
            domain.append(('area_id', '=', self.area.id))
        if self.division:
            domain.append(('division_id', '=', self.division.id))
        if self.district:
            domain.append(('district_id', '=', self.district.id))
        if self.upazila:
            domain.append(('upazila_id', '=', self.upazila.id))
        if self.union:
            domain.append(('union_id', '=', self.union.id))
        customers = self.env['res.partner'].sudo().search(domain)

        for customer in customers:
            customer.sudo().write({'discount_line_ids': [(6, 0, [])]})
            filb_values = []
            for line in self.discount_line_ids:
                prod = (0, 0, {'product_category': line.product_category.id,
                               'discount_percentage': line.discount_percentage,
                               'note': line.note,
                               'partner_id': customer.id
                               })
                filb_values.append(prod)
            customer.sudo().write({'discount_line_ids': filb_values})
        self.state = 'final'

    @api.constrains('discount_line_ids')
    def _check_duplicate_category_ids(self):
        for partner in self:
            category_ids = partner.discount_line_ids.mapped('product_category')
            if len(category_ids) != len(set(category_ids)):
                raise ValidationError('Duplicate product categories found in category discounts!')

class DiscountUpdateLine(models.Model):
    _name = 'discount.update.line'

    note = fields.Char(string='Discount Note')
    product_category = fields.Many2one('product.category', string='Product Category', required=True)
    discount_percentage = fields.Float(string='Discount %', default=0.0)
    discount_id = fields.Many2one('discount.update', string='Customer', required=True)

    _sql_constraints = [
        ('unique_product_category_partner_discount',
         'UNIQUE(product_category, discount_id)',
         'A duplicate product category for the same partner is not allowed!')
    ]