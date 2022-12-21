from odoo import api, fields, models, _
class RouteMaster(models.Model):
    _inherit = 'route.master'

    secondary_customer_ids = fields.One2many('secondary.customer.line', 'route', string='Customers')


class SecondCustomerLine(models.Model):
    _name = 'secondary.customer.line'

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.customer_code = self.customer_id.outlet_code

    route = fields.Many2one('route.master', string='Route ID')
    customer_id = fields.Many2one('customer.secondary', string='Customer name')
    customer_code = fields.Char('Customer Code')