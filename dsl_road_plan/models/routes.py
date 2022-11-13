from odoo import api, fields, models, _

class RouteMaster(models.Model):
    _name = 'route.master'
    _description = 'Sales Route Master'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Route Name")
    route_id = fields.Char(string='Route ID', copy=False, readonly=True)
    zone_id = fields.Many2one('res.zone', string="Zone")
    deputy_id = fields.Many2one('hr.employee', string="Deputy NSM")
    dsm_id = fields.Many2one('hr.employee', string="DSM")
    area_id = fields.Many2one('route.area', string="Area")
    territory_id = fields.Many2one('route.territory', string="Territory")
    remarks = fields.Char(string="Remarks")
    route_type = fields.Selection([
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('corporate', 'Corporate')
    ],  string='Route Type')
    primary_customer_ids = fields.One2many('primary.customer.line', 'route', string='Customers')
    corporate_customer_ids = fields.One2many('corporate.customer.line', 'route', string='Customers')
    # secondary_customer_ids = fields.One2many('secondary.customer.line', 'route', string='Customers')
    coverage = fields.Char(string="Coverage Area")

    @api.model
    def create(self, values):
        if values.get('route_id', _('New')) == _('New'):
            values['route_id'] = self.env['ir.sequence'].next_by_code('route.master')
        return super(RouteMaster, self).create(values)


class PrimaryCustomerLine(models.Model):
    _name = 'primary.customer.line'

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.customer_code = self.customer_id.code

    route = fields.Many2one('route.master', string='Route ID')
    customer_id = fields.Many2one('res.partner', string='Customer name',
                                  domain="[('olila_type', 'in', ('dealer','distributor'))]")
    customer_code = fields.Char('Customer Code')


class CorporateCustomerLine(models.Model):
    _name = 'corporate.customer.line'

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.customer_code = self.customer_id.code

    route = fields.Many2one('route.master', string='Route ID')
    customer_id = fields.Many2one('res.partner', string='Customer name',
                                  domain="[('olila_type', '=', 'corporater')]")
    customer_code = fields.Char('Customer Code')


# class SecondaryCustomerLine(models.Model):
#     _name = 'secondary.customer.line'
#
#     @api.onchange('customer_id')
#     def _onchange_customer_id(self):
#         if self.customer_id:
#             self.customer_code = self.customer_id.outlet_code
#
#     route = fields.Many2one('route.master', string='Route ID')
#     customer_id = fields.Many2one('customer.secondary', string='Customer name')
#     customer_code = fields.Char('Customer Code')


