# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class account_journal(models.Model):
    _inherit = "account.journal"

    def open_action_lc_direct_transfer(self):
    	return {
            'name': _('Direct Transfer'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'lc.direct.transfer',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('journal_id', '=', self.id)],
            'context': {'default_journal_id': self.id}
        }


class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        res = super(AccountMove, self).action_post()
        if self.lc_treansfer_id:
            self.lc_treansfer_id.state = 'paid'
        return res


class LCDirectTransfer(models.Model):
    _inherit = 'lc.direct.transfer'

    def button_post(self):
        move_line_dict = self._prepare_move_line()
        vals = {
            'move_type' : 'entry',
            'currency_id' : self.currency_id.id or False,
            'date' : self.date,
            'journal_id' : self.journal_id.id or False,
            'lc_treansfer_id' : self.id,
            'narration' : self.note,
            'line_ids': [(0, 0, line_data) for line_data in move_line_dict]
        }
        move_id = self.env['account.move'].create(vals)
        move_id.ref = self.ref
        self.moves_id = move_id.id


    def _prepare_move_line(self):
        move_line_dict = []
        company_id = self.env.user.company_id
        partner_id = self.line_ids.mapped('partner_id')
        journal = self.journal_id
        if journal.type == 'cash':
            account = journal.default_account_id
        elif journal.type == 'bank':
            if self.payment_type == 'income':
                account = journal.payment_debit_account_id
            else:
                account = journal.payment_credit_account_id
        if self.payment_type == 'income':
            move_line_dict.append({
                'account_id': account.id,
                'partner_id': partner_id and partner_id[0].id or False,
                'currency_id': self.currency_id and self.currency_id.id,
                'name': self.ref,
                'debit': sum(self.line_ids.mapped('amount')),
                'date_maturity': self.date,
                'ref': self.name,
                'date': self.date,
            })

        if self.payment_type == 'expense':
            move_line_dict.append({
                'account_id': account.id,
                'partner_id': partner_id and partner_id[0].id or False,
                'currency_id': self.currency_id and self.currency_id.id,
                'name': self.ref,
                'credit': sum(self.line_ids.mapped('amount')),
                'date_maturity': self.date,
                'ref': self.name,
                'date': self.date,
            })

        for line in self.line_ids:
            if self.payment_type == 'income':
                move_line_dict.append({
                    'account_id': line.account_id.id,
                    'partner_id': line.partner_id and line.partner_id.id or False,
                    'currency_id': line.currency_id and line.currency_id.id,
                    'name': line.ref,
                    'credit': line.amount,
                    'date_maturity': self.date,
                    'ref': line.ref,
                    'date': self.date,
                })
            if self.payment_type == 'expense':
                move_line_dict.append({
                    'account_id': line.account_id.id,
                    'partner_id': line.partner_id and line.partner_id.id or False,
                    'name': line.ref,
                    'currency_id': line.currency_id and line.currency_id.id,
                    'debit': line.amount,
                    'date_maturity': self.date,
                    'ref': line.ref,
                    'date': self.date,
                })
        return move_line_dict

    total_amount = fields.Float('Total Amount', compute="_compute_total_amount")
    moves_id = fields.Many2one('account.move', 'Journal Entry')
    word_num = fields.Char(string="Amount In Words:", compute='_amount_in_word')

    def _amount_in_word(self):
        for rec in self:
            rec.word_num = str(rec.currency_id.amount_to_text(rec.total_amount))

    @api.depends('line_ids')
    def _compute_total_amount(self):
        for record in self:
            total = 0.0
            for line in record.line_ids:
                total = total + line.amount
            record.total_amount = total
