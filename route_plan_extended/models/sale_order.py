# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    area_id = fields.Many2one('route.area', string="Area",  related='partner_id.area_id')
    territory_id = fields.Many2one('route.territory', string="Territory", related='partner_id.territory_id')
    route_id = fields.Many2one('route.master', string="Route ID", related='partner_id.route_id')
    division = fields.Selection([
        ('Dhaka', 'Dhaka'),
        ('Barisal', 'Barishal'),
        ('Chattogram', 'Chattogram'),
        ('Khulna', 'Khulna'),
        ('Rangpur', 'Rangpur'),
        ('Rajshahi', 'Rajshahi'),
        ('Mymensingh ', 'Mymensingh '),
        ('Sylhet ', 'Sylhet '),
    ], string='Division', related='partner_id.division')
    # district = fields.Selection([('Bagerhat', 'Bagerhat'),('Bandarban', 'Bandarban'),('Barguna', 'Barguna'),('Bhola', 'Bhola'),('Barisal', 'Barisal'),('Bogra', 'Bogra'),('Brahmanbaria', 'Brahmanbaria'),('Chandpur', 'Chandpur'),('Chittagong', 'Chittagong'),('Chuadanga', 'Chuadanga'),('Comilla', 'Comilla'),('Cox Bazar', 'Cox Bazar'),('Dhaka', 'Dhaka'),('Dinajpur', 'Dinajpur'),('Faridpur', 'Faridpur'),('Feni', 'Feni'),('Gaibandha', 'Gaibandha'),('Gazipur', 'Gazipur'),('Gopalganj', 'Gopalganj'),('Habiganj', 'Habiganj'),('Jaipurhat', 'Jaipurhat'),('Jamalpur', 'Jamalpur'),('Jessore', 'Jessore'),('Jhalakati', 'Jhalakati'),('Jhenaidah', 'Jhenaidah'),('Khagrachari', 'Khagrachari'),('Khulna', 'Khulna'),('Kishoreganj', 'Kishoreganj'),('Kurigram', 'Kurigram'),('Kushtia', 'Kushtia'),('Lakshmipur', 'Lakshmipur'),('Lalmonirhat', 'Lalmonirhat'),('Madaripur', 'Madaripur'),('Magura', 'Magura'),('Manikganj', 'Manikganj'),('Meherpur', 'Meherpur'),('Moulvibazar', 'Moulvibazar'),('Munshiganj', 'Munshiganj'),('Mymensingh', 'Mymensingh'),('Naogaon', 'Naogaon')('Narail', 'Narail'),('Narayanganj', 'Narayanganj'),('Narsingdi', 'Narsingdi'),('Natore', 'Natore'),('Nawabganj', 'Nawabganj'),('Netrakona', 'Netrakona'),('Nilphamari', 'Nilphamari'),('Noakhali', 'Noakhali'),('Pabna', 'Pabna'),('Panchagarh', 'Panchagarh'),('Parbattya Chattagram', 'Parbattya Chattagram'),('Patuakhali', 'Patuakhali'),('Pirojpur', 'Pirojpur'),('Rajbari', 'Rajbari'),('Rajshahi', 'Rajshahi'),
    #                              ('Rangpur', 'Rangpur'),('Satkhira', 'Satkhira'),('Shariatpur', 'Shariatpur'),('Sherpur', 'Sherpur'),('Sirajganj', 'Sirajganj'),('Sunamganj', 'Sunamganj'),('Sylhet', 'Sylhet'),('Tangail', 'Tangail'),('Thakurgaon', 'Thakurgaon')])

    # @api.depends('partner_id')
    # def _compute_area_from_customer(self):
    #     for record in self:
    #         record.area_id = record.partner_id.area_id.id
    #
    # @api.depends('partner_id')
    # def _compute_territory_from_customer(self):
    #     for record in self:
    #         record.territory_id = record.partner_id.territory_id.id
    #
    # @api.depends('partner_id')
    # def _compute_route_from_customer(self):
    #     for record in self:
    #         record.route_id = record.partner_id.route_id.id

    # @api.depends('partner_id')
    # def _compute_division_from_customer(self):
    #     for record in self:
    #         record.area_id = record.partner_id.area_id.id