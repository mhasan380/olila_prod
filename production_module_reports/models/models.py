# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class production_module_reports(models.Model):
#     _name = 'production_module_reports.production_module_reports'
#     _description = 'production_module_reports.production_module_reports'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
