from odoo import api, fields, models, _
class Zone(models.Model):
    _inherit = 'res.zone'

    responsible = fields.Many2one('hr.employee', string="Responsible", domain="[('type','=','rsm')]")
    territory_ids = fields.Many2many('route.territory', string="Territories")
    remarks = fields.Char(string="Remarks")