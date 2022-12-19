from odoo import models, fields, api, _

class Union(models.Model):
    _name = 'route.union'

    name = fields.Char(string="Union/Ward")
    divison_id = fields.Many2one('route.division')
    district_id = fields.Many2one('route.district')
    upazila_id = fields.Many2one('route.upazila', string="Upazila/Metropolitan/Thana")