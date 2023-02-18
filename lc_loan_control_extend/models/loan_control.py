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
                })
                order_line.append(order_line_vals)
        else:
            term_lines = self.amortisation_schedule_line(facility_size, interest_rate, payments_per_year, tenure)
            data_dict = term_lines.to_dict()
            order_line = [(5, 0, 0)]
            cumulative_interest = 0
            cumulative_installment = 0
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
                })
                order_line.append(order_line_vals)
        self.term_loan_lines = order_line