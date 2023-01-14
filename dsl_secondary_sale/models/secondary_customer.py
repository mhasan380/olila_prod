from datetime import datetime
from odoo import models, fields, api
import logging
import json

# Author - Md. Rafiul Hassan
# Daffodil Computers Ltd
# 26-09-2022

_logger = logging.getLogger(__name__)


class CustomerSecondary(models.Model):
    _name = 'customer.secondary'

    name = fields.Char(string='Customer Name')
    outlet_code = fields.Char(string='Outlet Code', index=True, copy=False, default="New", readonly=True)
    address = fields.Char(string='Customer Address')
    phone = fields.Char(string='Secondary Contact [Optional]')
    mobile = fields.Char(string='Customer Mobile', required=True)
    whats_app = fields.Char(string='WhatsApp No.')
    email = fields.Char(string='Customer Email')
    enabled = fields.Boolean("Enabled", default=True)

    partner_id = fields.Many2one('res.partner', string='Distributor', required=True)

    # partner_code = fields.Char(string='Distributor Code', related='partner_id.code')
    zone_id = fields.Many2one('res.zone', string='Zone', related='partner_id.zone_id')
    responsible_id = fields.Many2one('hr.employee', string='Responsible', required=True,
                                     related='partner_id.responsible')
    partner_code = fields.Char('Partner Code', related='partner_id.code', store=True)

    division_id = fields.Many2one('route.division', string='Division')
    district_id = fields.Many2one('route.district', string='District', domain="[('divison_id', '=', division_id)]")
    upazila_id = fields.Many2one('route.upazila', string='Upazila',
                                 domain="[('divison_id', '=', division_id), ('district_id', '=', district_id)]")
    union_id = fields.Many2one('route.union', string='Union',
                               domain="[('divison_id', '=', division_id), ('district_id', '=', district_id), ('upazila_id', '=', upazila_id)]")
    route_id = fields.Many2one('route.master', string='Route')
    so_market_id = fields.Many2one('route.area', string='SO Market', related='route_id.area_id')
    territory_id = fields.Many2one('route.territory', string='Territory', related='route_id.territory_id')
    region_id = fields.Many2one('res.zone', string='Region', related='route_id.zone_id')
    type = fields.Selection([
        ('crockeries', 'Crockeries'),
        ('plastic', 'Plastic'),
        ('decorator', 'Decorator'),
        ('restaurant', 'Restaurant'),
        ('residential_hotel', 'Residential Hotel'),
        ('community_center', 'Community Center'),
        ('resort', 'Resort'),
        ('one_to_ninety_nine', '1 To 99'),
        ('tea_stall', 'Tea Stall'),
        ('institute', 'Institute'),
        ('e_commerce', 'E-Commerce'),
        ('general_store', 'General Store'),
        ('departmental_store', 'Departmental Store')
    ], required=False, string='Customer Type')

    latitude = fields.Char('Lat', copy=False)
    longitude = fields.Char('Long', copy=False)
    create_location_url = fields.Char('Location Url', compute='_compute_create_location_url_for_map')

    @api.depends('latitude', 'longitude')
    def _compute_create_location_url_for_map(self):
        for record in self:
            link_builder = f'https://www.google.com/maps/place/{record.latitude}+{record.longitude}/@{record.latitude},{record.longitude},17z'
            if record.latitude and record.longitude:
                record.create_location_url = link_builder
            else:
                record.create_location_url = ''

    def preview_customer_location(self):
        if self.id:
            return {
                'type': 'ir.actions.act_url',
                'url': self.create_location_url,
                'target': 'new',
            }

    route_id_domain = fields.Char(
        compute="_compute_route_id_domain",
        readonly=True,
        store=False,
    )

    company_id = fields.Many2one('res.company')

    # stock_products = fields.One2many(comodel_name="products.customer.secondary", inverse_name="customer_id")
    @api.depends('latitude', 'longitude')
    def _compute_create_location_url_for_map(self):
        for record in self:
            link_builder = f'https://www.google.com/maps/place/{record.latitude}+{record.longitude}/@{record.latitude},{record.longitude},17z'
            if record.latitude and record.longitude:
                record.create_location_url = link_builder
            else:
                record.create_location_url = ''

    @api.onchange('partner_id')
    def _onchange_distributor(self):
        self.route_id = False

    @api.depends('partner_id')
    def _compute_route_id_domain(self):
        route_list = []
        for rec in self:
            route_customer_lines = rec.env['primary.customer.line'].sudo().search([('customer_id', '=', rec.partner_id.id)])
            for line in route_customer_lines:
                route_list.append(line.route.id)
            rec.route_id_domain = json.dumps(
                [('id', 'in', route_list)]
            )

    @api.onchange('division_id')
    def _onchange_division_id(self):
        self.district_id = False
        self.upazila_id = False
        self.union_id = False

    @api.onchange('district_id')
    def _onchange_district_id(self):
        self.upazila_id = False
        self.union_id = False

    @api.onchange('upazila_id')
    def _onchange_upazila_id(self):
        self.union_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            distributor = self.env['res.partner'].sudo().search([('id', '=', val['partner_id'])])
            raw_code = distributor.code or ''
            if raw_code and '/' in raw_code:
                x = raw_code.split('/')[1:]
                raw_code = x[0]
            print(raw_code)
            val['outlet_code'] = f"DT/{raw_code}/{self.env['ir.sequence'].next_by_code('customer.secondary') or '/'}"
        return super(CustomerSecondary, self).create(vals_list)

    def name_get(self):
        return [(customer.id,
                 '%s%s' % (customer.outlet_code and '[%s] ' % customer.outlet_code or '', customer.name)) for
                customer in self]

    # @api.onchange('responsible_id')
    # def _onchange_responsible_id(self):
    #     # if not self.responsible_id:
    #     self.partner_id = False
