# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AccountMove(models.Model):
    _inherit = 'account.move'

    word_num = fields.Char(string="Amount In Words:", compute='_amount_in_word')
    po_number = fields.Char(string="PO Number")
    po_date = fields.Date(string="PO Date")

    def _amount_in_word(self):
        for rec in self:
            rec.word_num = str(rec.currency_id.amount_to_text(rec.amount_total))

