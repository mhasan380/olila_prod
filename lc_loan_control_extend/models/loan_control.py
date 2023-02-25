# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd

from odoo import models, fields, api
from odoo.tools import float_compare, float_round


def PMT(rate, nper,pv, fv=0, type=0):
    if rate!=0:
        pmt = (rate*(fv+pv*(1+ rate)**nper))/((1+rate*type)*(1-(1+ rate)**nper))
    else:
        pmt = (-1*(fv+pv)/nper)
    return(pmt)


def IPMT(rate, per, nper,pv, fv=0, type=0):
    ipmt = -( ((1+rate)**(per-1)) * (pv*rate + PMT(rate, nper,pv, fv=0, type=0)) - PMT(rate, nper,pv, fv=0, type=0))
    return(ipmt)


def PPMT(rate, per, nper,pv, fv=0, type=0):
    ppmt = PMT(rate, nper,pv, fv=0, type=0) - IPMT(rate, per, nper, pv, fv=0, type=0)
    return(ppmt)

class AccountMove(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for rec in self:
            if rec.loan_ctrl_id and ('interest' in rec.ref):
                account_move = self.search([('loan_ctrl_id','=',rec.loan_ctrl_id.id)])
                rec.loan_ctrl_id.interest += sum(rec.mapped('amount_total_signed'))
        return super(AccountMove, self).action_post()

class LoanControllines(models.Model):
    _inherit = 'loan.control.lines'

    inti_balance = fields.Float('Int balance')

    @api.depends('payment_made','inti_balance')
    def _balance_compute(self):
        for rec in self:
            rec.balance = rec.inti_balance
            if rec.payment_made and rec.installment:
                rec.balance = rec.balance - rec.payment_made

    def account_move_create(self):
        term = self.term_loan_id
        journal_id = self.env['account.journal'].search([('type', '=', 'general')], limit=1)
        account_move = self.env['account.move'].create({
            'ref': term.number + 'interest',
            'journal_id':journal_id.id,
            'loan_ctrl_id': self.id,
            'loan_ctrl_name': term.number + '(' + str(self.sequence) + ')',
        })
        aml_obj = self.env['account.move.line'].with_context(
            check_move_validity=False)
        move_product_lines = aml_obj.create([
            {
                'name': term.bank_account_id.name,
                'move_id': account_move.id,
                'account_id': term.loan_account_id.id,
                'debit': 0,
                'credit': 0,
            },
            {
                'name': term.interest_expense_id.name,
                'move_id': account_move.id,
                'account_id': term.interest_expense_id.id,
                'debit': 0,
                'credit': 0,
            }
        ])
        # account_move.action_post()

    def add_interest_journal(self):
        for rec in self:
            rec.account_move_create()



class LoanControl(models.Model):
    _inherit = 'loan.control'

    def amortisation_schedule(self, amount, annualinterestrate, paymentsperyear, years):
        if paymentsperyear == 1:
            rng = pd.date_range(self.due_date, periods=years * float(paymentsperyear), freq='12M')
        elif paymentsperyear == 2:
            rng = pd.date_range(self.due_date, periods=years * float(paymentsperyear), freq='6M')
        elif paymentsperyear == 4:
            rng = pd.date_range(self.due_date, periods=years * float(paymentsperyear), freq='3M')
        elif paymentsperyear == 12:
            rng = pd.date_range(self.due_date, periods=years * float(paymentsperyear), freq='M')
        elif paymentsperyear == 52:
            rng = pd.date_range(self.due_date, periods=years * float(paymentsperyear), freq='W')
        else:
            rng = pd.date_range(self.due_date, periods=years * float(paymentsperyear), freq='D')
        rng.name = "Payment_Date"
        df = pd.DataFrame({'Principal': [
            PPMT(annualinterestrate / paymentsperyear, i + 1, int(float(paymentsperyear) * years), amount) for i in
            range(int(float(paymentsperyear) * years))],
                           'Interest': [
                               IPMT(annualinterestrate / paymentsperyear, i + 1, int(float(paymentsperyear) * years),
                                    amount) for i in range(int(float(paymentsperyear) * years))]})
        df['Instalment'] = df.Principal + df.Interest
        df['Balance'] = amount + np.cumsum(df.Principal)
        df['Payment_Date'] = rng
        return (df)

    def amortisation_schedule_line(self, amount, annualinterestrate, paymentsperyear, years):
        rng = pd.date_range(self.due_date, periods=years * float(paymentsperyear), freq='M')
        rng.name = "Payment_Date"

        df = pd.DataFrame(
            {'Principal': [(amount / (float(paymentsperyear) * years)) for i in range(float(paymentsperyear) * years)],
             'Interest': [IPMT(annualinterestrate / paymentsperyear, i + 1, float(paymentsperyear) * years, amount) for
                          i in range(float(paymentsperyear) * years)]})
        df['Instalment'] = abs(df.Principal) + abs(df.Interest)
        df['Balance'] = abs(amount) - abs(np.cumsum(df.Principal))
        df['Payment_Date'] = rng
        return (df)

    def compute_loan_term(self):
        facility_size = self.facility_size
        interest_rate = float(self.interest_rate / 100)
        tenure = self.tenure
        payments_per_year = int(self.payments_per_year)
        if self.instalment_size == 'pp':
            term_lines = self.amortisation_schedule(facility_size, interest_rate, payments_per_year, tenure)
            data_dict = term_lines.to_dict()
            order_line = [(5, 0, 0)]
            cumulative_interest = 0
            intl_balance = self.facility_size
            for key in data_dict['Principal']:
                # import pdb;pdb.set_trace();
                cumulative_interest += abs(data_dict['Interest'][key])
                rounding = 2
                order_line_vals = (0, 0, {
                    'sequence': key + 1,
                    'principal': abs(data_dict['Principal'][key]),
                    'interest': abs(data_dict['Interest'][key]),
                    'installment': abs(data_dict['Instalment'][key]),
                    'ending_balance': abs(data_dict['Balance'][key]),
                    'cumulative_interest': cumulative_interest,
                    'cumulative_installment': abs(data_dict['Instalment'][key]) * (key + 1),
                    'due_date': data_dict['Payment_Date'][key],
                    'inti_balance': intl_balance + cumulative_interest
                })
                order_line.append(order_line_vals)
                print(order_line_vals)
        else:
            term_lines = self.amortisation_schedule_line(facility_size, interest_rate, payments_per_year, tenure)
            data_dict = term_lines.to_dict()
            order_line = [(5, 0, 0)]
            cumulative_interest = 0
            cumulative_installment = 0
            intl_balance = self.facility_size
            for key in data_dict['Principal']:
                cumulative_interest += abs(data_dict['Interest'][key])
                cumulative_installment += abs(data_dict['Instalment'][key])
                rounding = 2
                order_line_vals = (0, 0, {
                    'sequence': key + 1,
                    'principal': abs(data_dict['Principal'][key]),
                    'interest': abs(data_dict['Interest'][key]),
                    'installment': abs(data_dict['Instalment'][key]),
                    'ending_balance': abs(data_dict['Balance'][key]),
                    'cumulative_interest': cumulative_interest,
                    'cumulative_installment': cumulative_installment,
                    'due_date': data_dict['Payment_Date'][key],
                    'inti_balance': intl_balance + cumulative_interest
                })
                order_line.append(order_line_vals)
                print(order_line_vals)
        self.term_loan_lines = order_line