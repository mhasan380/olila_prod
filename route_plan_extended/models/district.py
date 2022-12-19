from odoo import models, fields, api, _


class District(models.Model):
    _name = 'route.district'

    name = fields.Char(string="District Name")
    divison_id = fields.Many2one('route.division')