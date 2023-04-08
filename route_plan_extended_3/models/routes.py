from odoo import api, fields, models, _

class RouteMaster(models.Model):
    _inherit = 'route.master'

    def assign_customers(self):
        if self.route_type == 'secondary':
            customers = []
            customer_list = self.env['customer.secondary'].search([('route_id', '=', self.id)])
            for customer in customer_list:
                if customer.id not in customers:
                    customers.append(customer.id)
            self.update({
                'secondary_customer_ids': [(6, 0, customers)],
            })