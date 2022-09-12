# -*- coding: utf-8 -*-

from odoo import models, fields, api, _

class CustomerDiscountWizard(models.TransientModel):
    _name = 'customer.discount.wizard'

    customer_type = fields.Selection(selection=[('corporater', 'Corporate'), ('dealer', 'Dealer'), ('distributor', 'Distributor')], string="Customer Type")
    discount_percent = fields.Float('Discount Percentage')

    def update_discount(self):
        customers = self.env['res.partner'].search([('is_customer', '=', True)])
        for customer in customers:
            if customer.olila_type == self.customer_type:
                customer.discount = self.discount_percent
