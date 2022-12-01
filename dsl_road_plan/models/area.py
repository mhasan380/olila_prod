from odoo import api, fields, models, _

class RouteArea(models.Model):
    _name = 'route.area'
    _description = 'Sales Route Area'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    area_id = fields.Char(string='Area ID',copy= False, readonly= True)
    responsible = fields.Many2one('hr.employee', string="Responsible")
    remarks = fields.Char(string="Remarks")
    customer_line_ids = fields.One2many('area.customer.line', 'area', string='Customers')
    total_customer = fields.Integer(compute='_compute_total_customer')

    def _compute_total_customer(self):
        for record in self:
            record.total_customer = len(self.customer_line_ids)

    @api.model
    def create(self, values):
        if values.get('area_id', _('New')) == _('New'):
            values['area_id'] = self.env['ir.sequence'].next_by_code('route.area')
        return super(RouteArea, self).create(values)


class AreaCustomerLine(models.Model):
    _name = 'area.customer.line'

    @api.onchange('area')
    def _onchange_area(self):
        if self.area:
            return {'domain': {'customer_id': [('responsible', '=', self.area.responsible)]}}

    @api.onchange('customer_id')
    def _onchange_customer_id(self):
        if self.customer_id:
            self.customer_code = self.customer_id.code

    area = fields.Many2one('route.area', string='Area ID')
    customer_id = fields.Many2one('res.partner', string='Customer name')
    customer_code = fields.Char('Customer Code')

