# -*- coding: utf-8 -*-
import operator as py_operator

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, date, timedelta

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}



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
            'context': {'default_journal_id': self.id, 'default_journal_type': self.type}
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
        self.state = 'journal'


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

            for line in self.line_ids:
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


        return move_line_dict

    total_amount = fields.Float('Total Amount', compute="_compute_total_amount" ,search='_search_total_amount')
    moves_id = fields.Many2one('account.move', 'Journal Entry')
    word_num = fields.Char(string="Amount In Words:", compute='_amount_in_word')
    payee = fields.Char('Payee/Receiver')
    journal_type = fields.Selection([('bank','Bank'), ('cash','Cash')], string='Journal Type')
    cheque_no = fields.Char('Cheque No')
    cheque_date = fields.Date('Cheque Date')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'),('journal', 'Journal Entry'), ('paid', 'Paid'), ('cancel', 'Cancel')],
                             string='Status', required=True, readonly=True, copy=False, tracking=True, default='draft')
    date = fields.Date(string="Date", default=datetime.today(), required=True)



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

    def change_journal_num(self):
        for rec in self:
            if rec.state == 'paid':
                rec.moves_id = self.env['account.move'].search([('lc_treansfer_id', '=', rec.id)], limit=1).id


    def print_cash_vouchar(self):
        return self.env.ref('direct_transfer_extend.action_olila_cash_voucher_report').report_action(self)

    def print_bank_vouchar(self):
        return self.env.ref('direct_transfer_extend.action_olila_bank_voucher_report').report_action(self)
    def _search_total_amount(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_total_amount(operator, value, 'total_amount')

    def _search_product_total_amount(self, operator, value, field):
        # TDE FIXME: should probably clean the search methods
        # to prevent sql injections
        if field not in ('total_amount'):
            raise UserError(_('Invalid domain left operand %s', field))
        if operator not in ('<', '>', '=', '!=', '<=', '>='):
            raise UserError(_('Invalid domain operator %s', operator))
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s', value))

        # TODO: Still optimization possible when searching virtual quantities
        ids = []
        # Order the search on `id` to prevent the default order on the product name which slows
        # down the search because of the join on the translation table to get the translated names.
        for product in self.with_context(prefetch_fields=False).search([], order='id'):
            if OPERATORS[operator](product[field], value):
                ids.append(product.id)
        return [('id', 'in', ids)]

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(LCDirectTransfer, self).read_group(domain, fields, groupby, offset=offset, limit=limit,
                                                      orderby=orderby,
                                                      lazy=lazy)
        if 'total_amount' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_net_value = 0.0
                    for record in lines:
                        total_net_value += record.total_amount

                    line['total_amount'] = total_net_value

        return res
