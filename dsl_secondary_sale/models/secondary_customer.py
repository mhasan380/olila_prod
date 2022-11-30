from datetime import datetime
from odoo import models, fields, api
import logging

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
    email = fields.Char(string='Customer Email')
    enabled = fields.Boolean("Enabled", default=True)

    partner_id = fields.Many2one('res.partner', string='Distributor', required=True)
    # partner_code = fields.Char(string='Distributor Code', related='partner_id.code')
    zone_id = fields.Many2one('res.zone', string='Zone', related='partner_id.zone_id')
    responsible_id = fields.Many2one('hr.employee', string='Responsible', required=True,
                                     related='partner_id.responsible')
    partner_code = fields.Char('Partner Code', related='partner_id.code', store =True)
    company_id = fields.Many2one('res.company')

    # stock_products = fields.One2many(comodel_name="products.customer.secondary", inverse_name="customer_id")

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
