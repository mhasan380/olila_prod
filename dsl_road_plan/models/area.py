from odoo import api, fields, models, _

class RouteArea(models.Model):
    _name = 'route.area'
    _description = 'Sales Route Area'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    area_id = fields.Char(string='ID',copy= False, readonly= True)
    responsible = fields.Many2one('hr.employee', string="Responsible", domain="[('type','=','so')]")
    remarks = fields.Char(string="Remarks")
    customer_line_ids = fields.One2many('area.customer.line', 'area', string='Customers')
    zone_id = fields.Many2one('res.zone', string="Zone")
    territory_id = fields.Many2one('route.territory', string="Territory")


    @api.model
    def create(self, values):
        if values.get('area_id', _('New')) == _('New'):
            values['area_id'] = self.env['ir.sequence'].next_by_code('route.area')
        return super(RouteArea, self).create(values)


class AreaCustomerLine(models.Model):
    _name = 'area.customer.line'


    @api.onchange('route_id')
    def _onchange_route_id(self):
        if self.route_id:
            self.route_code = self.route_id.route_id
            self.coverage_area = self.route_id.coverage

    area = fields.Many2one('route.area', string='Area ID')
    route_id = fields.Many2one('route.master', string='Route name')
    route_code = fields.Char('Route ID')
    coverage_area = fields.Char('Coverage Area')

