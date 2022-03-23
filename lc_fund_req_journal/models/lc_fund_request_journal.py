# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class LCOpeningFundRequisition(models.Model):
    _inherit = 'lc.opening.fund.requisition'

    def _move_count(self):
        for rec in self:
            move_ids = self.env['account.move'].search([('lc_fund_req_id', '=', rec.id)])
            rec.move_count = len(move_ids.ids)

    def view_journal_entry(self):
        move_ids = self.env['account.move'].search([('lc_fund_req_id', '=', self.id)])
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'view_id': False,
            'type': 'ir.actions.act_window',
            'domain': [('id', 'in', move_ids.ids)],
        }

    lc_opening_bank = fields.Many2one('account.journal',string="LC Opening Bank")
    lc_margin_account = fields.Many2one('account.account',string="LC Margin Account")
    lc_com_account = fields.Many2one('account.account', string="LC Comission Account")
    lc_fund_taxes = fields.Many2one('account.account', string="LC TAX Account")
    lc_lcfr_other_charges = fields.Many2one('account.account', string="Other Charges Account")
    move_count = fields.Integer(compute='_move_count', string='#Move')




    def _prepare_move_line1(self):
        move_line_dict = []
        amount = 0.0
        move_line_dict.append({
            'account_id': self.lc_opening_bank.payment_credit_account_id.id or False,
            'credit': self.margin,
            # 'date_maturity': self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict.append({
            'account_id': self.lc_margin_account.id or False,
            'debit': self.margin,
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })

        return move_line_dict

    def _prepare_move_line2(self):
        move_line_dict2 = []
        amount = 0.0
        move_line_dict2.append({
            'account_id': self.lc_opening_bank.suspense_account_id.id or False,
            'credit': (
                        self.commission + self.source_tax + self.vat_on_commission + self.pt_charge + self.other_charges),
            # 'date_maturity': self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict2.append({
            'account_id': self.lc_com_account.id or False,
            'debit': self.commission,
            'name': 'Comission'
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict2.append({
            'account_id': self.lc_fund_taxes.id or False,
            'debit': self.source_tax,
            'name': 'Source Tax'
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict2.append({
            'account_id': self.lc_fund_taxes.id or False,
            'debit': self.vat_on_commission,
            'name': 'VAT on Comission'
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict2.append({
            'account_id': self.lc_lcfr_other_charges.id or False,
            'debit': (self.pt_charge + self.other_charges),
            'name': 'PT and Other Charges'
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })
        return move_line_dict2

    def button_paid(self):
        move_lines1 = self._prepare_move_line1()
        vals = {
            'move_type': 'entry',
            'date': self.lc_requisition_date,
            'journal_id': self.env['account.journal'].search([('name','=','Miscellaneous Operations')], limit=1).id,
             'lc_fund_req_id' : self.id,
            'line_ids': [(0, 0, line_data) for line_data in move_lines1]
        }
        move_id1 = self.env['account.move'].create(vals)
        move_id1.ref = 'LC Margin'

        move_lines2 = self._prepare_move_line2()
        vals2 = {
            'move_type': 'entry',
            'date': self.lc_requisition_date,
            'journal_id': self.env['account.journal'].search([('name', '=', 'Miscellaneous Operations')], limit=1).id,
            'lc_fund_req_id': self.id,
            'line_ids': [(0, 0, line_data) for line_data in move_lines2]
        }
        move_id2 = self.env['account.move'].create(vals2)
        move_id2.ref = 'LC Comission and Other Charges'
        self.write({'state': 'paid'})
        return True



