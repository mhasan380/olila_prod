# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SaleOrder(models.Model):
    _inherit = 'sale.order'

    sales_ref_id = fields.Many2one('hr.employee',string="Sales Reference")

    def change_invoice_state(self):
        self.invoice_status = 'invoiced'

