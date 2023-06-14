# -*- coding: utf-8 -*-
from odoo import models, fields, api,_
from odoo.exceptions import UserError

class CfAggent(models.Model):
    _inherit = 'res.cf.aggent'

    def _prepare_move_line(self):
        move_line_dict = []
        amount = 0.0
        company_id = self.env.user.company_id
        if not company_id.lc_agent_charges_account:
            raise UserError(_("Cannot create journal entry . please configure account in company"))
        for line in self.agents_charge_ids:
            move_line_dict.append({
                'account_id' : line.product_id.property_account_expense_id.id or line.product_id.categ_id.property_account_expense_categ_id.id or False,
                'partner_id' : self.aggent_partner_id.id or False,
                'name' : line.product_id.display_name if line.product_id else '/',
                'currency_id' : self.currency_id.id,
                'debit' : line.sub_total,
                'date_maturity' : self.move_date,
                'ref' : self.name,
                'date' : self.move_date,
            })
            amount += line.sub_total
        move_line_dict.append({
            'account_id' : self.aggent_partner_id and self.aggent_partner_id.property_account_payable_id.id or False,
            'partner_id' : self.aggent_partner_id.id or False,
            'name' : self.opening_id.lc_no,
            'currency_id' : self.currency_id.id,
            'credit' : amount,
            'date_maturity' : self.move_date,
            'ref' : self.name,
            'date' : self.move_date,
        })
        return move_line_dict