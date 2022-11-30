from odoo import api, fields, models, _

class RouteTerritory(models.Model):
    _name = 'route.territory'
    _description = 'Sales Route Territory'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Name")
    territory_id = fields.Char(string='Territory ID',copy= False, readonly= True)
    zone_id = fields.Many2one('res.zone', string="Region")
    responsible = fields.Many2one('hr.employee', string="Responsible", domain="[('type','=','tso')]")
    remarks = fields.Char(string="Remarks")
    area_ids = fields.Many2many('route.area', string="Areas")


    @api.model
    def create(self, values):
        if values.get('territory_id', _('New')) == _('New'):
            values['territory_id'] = self.env['ir.sequence'].next_by_code('route.territory')
        return super(RouteTerritory, self).create(values)