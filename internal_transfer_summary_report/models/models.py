# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class internal_transfer_summary_report(models.Model):
#     _name = 'internal_transfer_summary_report.internal_transfer_summary_report'
#     _description = 'internal_transfer_summary_report.internal_transfer_summary_report'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
