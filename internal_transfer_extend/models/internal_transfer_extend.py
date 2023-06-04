# -*- coding: utf-8 -*-

from odoo import api, fields, models

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'
    remarks = fields.Char(string='remarks')


class StockMove(models.Model):
    _inherit = "stock.move"
    remarks = fields.Char(string='remarks')
