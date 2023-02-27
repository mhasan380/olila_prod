# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class daily_projection(models.Model):
#     _name = 'daily_projection.daily_projection'
#     _description = 'daily_projection.daily_projection'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
