# -*- coding: utf-8 -*-

# from odoo import models, fields, api


# class 3rd_party_depot(models.Model):
#     _name = '3rd_party_depot.3rd_party_depot'
#     _description = '3rd_party_depot.3rd_party_depot'

#     name = fields.Char()
#     value = fields.Integer()
#     value2 = fields.Float(compute="_value_pc", store=True)
#     description = fields.Text()
#
#     @api.depends('value')
#     def _value_pc(self):
#         for record in self:
#             record.value2 = float(record.value) / 100
