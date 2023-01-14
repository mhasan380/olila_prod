from odoo import api, fields, models
from datetime import date


class CheckList(models.Model):
    _inherit = 'rode.list'

    secondary_customer = fields.Many2one('customer.secondary', string="Secondary Customer")
