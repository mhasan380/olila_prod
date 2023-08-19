# -*- coding: utf-8 -*-

import logging
import ast

from odoo import models, fields, api, _
from odoo.tools.misc import format_date

class AccountBankReconciliationReport(models.AbstractModel):
    _inherit = 'account.bank.reconciliation.report'

    @api.model
    def _get_payment_report_lines(self, options, journal):
        ''' Retrieve the journal items used by the payment lines that are not yet reconciled and then, need to be
        displayed inside the report.
        :param options: The report options.
        :param journal: The journal as an account.journal record.
        :return:        The report lines for sections about statement lines.
        '''
        company_currency = journal.company_id.currency_id
        journal_currency = journal.currency_id if journal.currency_id and journal.currency_id != company_currency else False
        report_currency = journal_currency or company_currency
        unfold_all = options.get('unfold_all') or (self._context.get('print_mode') and not options['unfolded_lines'])

        accounts = journal.payment_debit_account_id + journal.payment_credit_account_id
        if not accounts:
            return [], []

        # Allow user managing payments without any statement lines.
        # In that case, the user manages transactions only using the register payment wizard.
        if journal.default_account_id in accounts:
            return [], []

        current_date = fields.Date.from_string(options['date']['date_to'])
        if current_date < fields.Date.context_today(self):
            # If the user selected a date in the past, filter payments as well.
            new_options = options
        else:
            # Include payments made in the future.
            new_options = {**options, 'date': None}

        tables, where_clause, where_params = self.with_company(journal.company_id)._query_get(new_options, domain=[
            ('journal_id', '=', journal.id),
            ('account_id', 'in', accounts.ids),
            '|', ('payment_id.is_matched', '=', False), ('reconciled', '=', False)
        ])

        self._cr.execute('''
                SELECT
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    account_move_line.move_id,
                    account_move_line.currency_id,
                    account_move_line__move_id.name,
                    account_move_line__move_id.ref,
                    account_move_line__move_id.date,
                    account.reconcile AS is_account_reconcile,
                    SUM(account_move_line.amount_residual) AS amount_residual,
                    SUM(account_move_line.balance) AS balance,
                    SUM(account_move_line.amount_residual_currency) AS amount_residual_currency,
                    SUM(account_move_line.amount_currency) AS amount_currency
                FROM ''' + tables + '''
                JOIN account_account account ON account.id = account_move_line.account_id
                WHERE ''' + where_clause + '''
                GROUP BY 
                    account_move_line.account_id,
                    account_move_line.payment_id,
                    account_move_line.move_id,
                    account_move_line.currency_id,
                    account_move_line__move_id.name,
                    account_move_line__move_id.ref,
                    account_move_line__move_id.date,
                    account.reconcile
                ORDER BY account_move_line__move_id.date DESC, account_move_line.payment_id DESC
            ''', where_params)

        plus_report_lines = []
        less_report_lines = []
        plus_total = 0.0
        less_total = 0.0

        for res in self._cr.dictfetchall():
            amount_currency = res['amount_residual_currency'] if res['is_account_reconcile'] else res['amount_currency']
            balance = res['amount_residual'] if res['is_account_reconcile'] else res['balance']

            if res['currency_id'] and journal_currency and res['currency_id'] == journal_currency.id:
                # Foreign currency, same as the journal one.

                if journal_currency.is_zero(amount_currency):
                    continue

                monetary_columns = [
                    {'name': ''},
                    {'name': ''},
                    {
                        'name': self.format_value(amount_currency, journal_currency),
                        'no_format': amount_currency,
                    },
                ]

            elif res['currency_id']:
                # Payment using a foreign currency that needs to be converted to the report's currency.

                foreign_currency = self.env['res.currency'].browse(res['currency_id'])
                journal_balance = company_currency._convert(balance, report_currency, journal.company_id,
                                                            options['date']['date_to'])

                if foreign_currency.is_zero(amount_currency) and company_currency.is_zero(balance):
                    continue

                monetary_columns = [
                    {
                        'name': self.format_value(amount_currency, foreign_currency),
                        'no_format': amount_currency,
                    },
                    {'name': foreign_currency.name},
                    {
                        'name': self.format_value(journal_balance, report_currency),
                        'no_format': journal_balance,
                    },
                ]

            elif not res['currency_id'] and journal_currency:
                # Single currency in the payment but a foreign currency on the journal.

                journal_balance = company_currency._convert(balance, journal_currency, journal.company_id,
                                                            options['date']['date_to'])

                if company_currency.is_zero(balance):
                    continue

                monetary_columns = [
                    {
                        'name': self.format_value(balance, company_currency),
                        'no_format': balance,
                    },
                    {'name': company_currency.name},
                    {
                        'name': self.format_value(journal_balance, journal_currency),
                        'no_format': journal_balance,
                    },
                ]

            else:
                # Single currency.

                if company_currency.is_zero(balance):
                    continue

                monetary_columns = [
                    {'name': ''},
                    {'name': ''},
                    {
                        'name': self.format_value(balance, journal_currency),
                        'no_format': balance,
                    },
                ]

            pay_report_line = {
                'id': res['move_id'],
                'name': res['name'],
                'columns': self._apply_groups([
                                                  {'name': format_date(self.env, res['date']), 'class': 'date'},
                                                  {'name': res['ref']},
                                              ] + monetary_columns),
                'model': 'account.move',
                'caret_options': 'account.move',
                'level': 3,
            }

            residual_amount = monetary_columns[2]['no_format']
            if res['account_id'] == journal.payment_debit_account_id.id:
                pay_report_line['parent_id'] = 'plus_unreconciled_payment_lines'
                plus_total += residual_amount
                plus_report_lines.append(pay_report_line)
            else:
                pay_report_line['parent_id'] = 'less_unreconciled_payment_lines'
                less_total += residual_amount
                less_report_lines.append(pay_report_line)

            is_parent_unfolded = unfold_all or pay_report_line['parent_id'] in options['unfolded_lines']
            if not is_parent_unfolded:
                pay_report_line['style'] = 'display: none;'

        return (
            self._build_section_report_lines(options, journal, plus_report_lines, plus_total,
                                             _("(+) Outstanding Receipts"),
                                             _("Transactions(+) that were entered into Odoo (%s), but not yet reconciled (Payments triggered by "
                                               "invoices/refunds or manually)") % journal.payment_debit_account_id.display_name,
                                             ),
            self._build_section_report_lines(options, journal, less_report_lines, less_total,
                                             _("(-) Outstanding Payments"),
                                             _("Transactions(-) that were entered into Odoo (%s), but not yet reconciled (Payments triggered by "
                                               "bills/credit notes or manually)") % journal.payment_credit_account_id.display_name,
                                             ),
        )




