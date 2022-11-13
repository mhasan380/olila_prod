from odoo import api, fields, models, _

class RouteDay(models.Model):
    _name = 'route.day'
    _description = 'Sales Route Days'

    name = fields.Char(string="Day Name")