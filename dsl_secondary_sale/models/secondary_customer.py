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
    code = fields.Char(string='Code', index=True, copy=False, default="New", readonly=True)
    address = fields.Char(string='Customer Address')
    phone = fields.Char(string='Customer Phone [Optional]')
    mobile = fields.Char(string='Customer Mobile', required=True)
    email = fields.Char(string='Customer Email')
    enabled = fields.Boolean("Enabled", default=True)

    partner_id = fields.Many2one('res.partner', string='Primary Customer', required=True)
    responsible_id = fields.Many2one('hr.employee', string='Responsible', required=True,
                                     related='partner_id.responsible')
    partner_code = fields.Char('Partner Code', related='partner_id.code')
    company_id = fields.Many2one('res.company')

    # stock_products = fields.One2many(comodel_name="products.customer.secondary", inverse_name="customer_id")

    @api.model_create_multi
    def create(self, vals_list):
        for val in vals_list:
            val['code'] = self.env['ir.sequence'].next_by_code('customer.secondary') or '/'
        return super(CustomerSecondary, self).create(vals_list)

    # @api.onchange('responsible_id')
    # def _onchange_responsible_id(self):
    #     # if not self.responsible_id:
    #     self.partner_id = False
