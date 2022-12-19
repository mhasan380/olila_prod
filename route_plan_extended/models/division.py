from odoo import models, fields, api, _

class Division(models.Model):
    _name = 'route.division'

    name = fields.Char(string="Division Name")