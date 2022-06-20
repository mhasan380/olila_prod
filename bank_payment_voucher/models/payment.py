# -*- coding: utf-8 -*-

from odoo import models, fields, api

class AccountPayment(models.Model):
    _inherit = "account.payment"

    word_num = fields.Char(string="Amount In Words:", compute='_amount_in_word')

    def _amount_in_word(self):
        for rec in self:
            rec.word_num = str(rec.currency_id.amount_to_text(rec.amount))


    def print_bank_payment(self):
        return self.env.ref('bank_payment_voucher.action_bank_vendor_voucher_report').report_action(self)

