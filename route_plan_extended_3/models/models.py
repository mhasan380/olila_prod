# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class route_plan_extended_3(models.Model):
#     _name = 'route_plan_extended_3.route_plan_extended_3'
#     _description = 'route_plan_extended_3.route_plan_extended_3'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
