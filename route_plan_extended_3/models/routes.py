from odoo import api, fields, models, _

class RouteMaster(models.Model):
    _inherit = 'route.master'

    def assign_customers(self):
        if self.route_type == 'secondary':
            self.secondary_customer_ids = [(6, 0, [])]
            customers = []
            customer_list = self.env['customer.secondary'].search([('route_id', '=', self.id)])
            for customer in customer_list:
                prod = (0, 0, {'customer_id': customer.id,
                               'customer_code': customer.outlet_code,
                               })
                customers.append(prod)
        self.write({'secondary_customer_ids': customers})


    def auto_assign(self):
        routes = self.env['route.master'].search([])
        for rec in routes:
            rec.assign_customers()