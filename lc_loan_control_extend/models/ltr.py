# -*- coding: utf-8 -*-

from datetime import timedelta, datetime

from odoo import models, fields, api

class LtrControl(models.Model):
    _inherit = 'ltr.control'

    def change_ltr_state(self):
        for record in self:
            record.overdue_status = 'run'

    lc_num = fields.Char('LC Number')

    @api.onchange('lc_number')
    def onchange_lc_number(self):
        for ltr in self:
            if ltr.lc_number:
                ltr.lc_num = ltr.lc_number.lc_no

    # @api.model
    # def create(self, vals):
    #     if vals.get('lc_num'):
    #         lc = self.env['lc.opening'].search([('lc_no', '=', vals['lc_num'])])
    #         vals.update({'lc_number': lc.id})

    def overdue_check(self):
        today = fields.date.today()
        ltr_records = self.env['ltr.control'].search([('overdue_status', '=', 'run')])
        for rec in ltr_records:
            if rec.due_date < today:
                rec.overdue_status = 'due'




class LtrInterestLines(models.Model):
    _inherit = 'ltr.interest.lines'

    def interest_journal_entry(self):
        ref = self.ltr_id.number
        journal_id = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        account_move = self.env['account.move'].create({
            'ref': ref,
            'journal_id':journal_id.id,
            'date': self.date

        })
        aml_obj = self.env['account.move.line'].with_context(
            check_move_validity=False)
        move_product_lines = aml_obj.create([
            {
                'name': ref,
                'move_id': account_move.id,
                'account_id': self.ltr_id.ltr_account_id.id,
                'debit': 0,
                'credit': (self.interest_charged + self.bank_charge),
            },
            {
                'name': ref,
                'move_id': account_move.id,
                'account_id': self.ltr_id.interest_account_id.id,
                'debit': self.interest_charged,
                'credit': 0,
            },

            {
                'name': ref,
                'move_id': account_move.id,
                'account_id': self.ltr_id.bank_charge_id.id,
                'debit': self.bank_charge,
                'credit': 0,
            },

        ])
        self.ltr_id.interest_charged = self.ltr_id.interest_charged + self.interest_charged
        self.ltr_id.bank_charge = self.ltr_id.bank_charge + self.bank_charge
        self.ltr_id.ltr_balance = self.ltr_id.ltr_balance + self.interest_charged + self.bank_charge
        self.state = 'done'


class LtrPaymentLines(models.Model):
    _inherit = 'ltr.payment.lines'

    payment_journal = fields.Many2one('account.journal')

    def account_move_creation(self):
        ref = self.ltr_id.number
        journal_id = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        account_move = self.env['account.move'].create({
            'ref': ref,
            'journal_id':journal_id.id,
            'date': self.date

        })
        aml_obj = self.env['account.move.line'].with_context(
            check_move_validity=False)
        move_product_lines = aml_obj.create([
            {
                'name': ref,
                'move_id': account_move.id,
                'account_id': self.payment_journal.payment_credit_account_id.id,
                'debit': 0,
                'credit': self.payment,
            },
            {
                'name': ref,
                'move_id': account_move.id,
                'account_id': self.ltr_id.ltr_account_id.id,
                'debit': self.payment,
                'credit': 0,
            },

        ])
        self.ltr_id.payment = self.ltr_id.payment + self.payment
        self.state = 'done'
        self.ltr_id.ltr_balance = self.ltr_id.ltr_balance - self.payment
        if self.ltr_id.ltr_balance == 0:
            self.ltr_id.overdue_status = 'paid'