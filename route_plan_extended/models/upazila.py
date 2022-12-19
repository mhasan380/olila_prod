from odoo import models, fields, api, _

class Upazila(models.Model):
    _name = 'route.upazila'

    name = fields.Char(string="Upazila/Metropolitan/Thana")
    divison_id = fields.Many2one('route.division')
    district_id = fields.Many2one('route.district')


