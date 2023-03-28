# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class PurchaseLcAmmendment(models.Model):
    _inherit="purchase.lc.ammendment"

    foreign_vat = fields.Float('Vat Revenue on Foreign')
    other_vat = fields.Float('Vat Revenue on Other')
    source_tax = fields.Float('Tax on Source')
    postage = fields.Float('Postage and Telegram')

    total_charges = fields.Float(string='Total', compute='_compute_total_charges')

    @api.depends('ammendment_charges','foreign_vat','other_vat','source_tax','postage')
    def _compute_total_charges(self):
        for rec in self:
            rec.total_charges = rec.ammendment_charges + rec.foreign_vat + rec.other_vat + rec.source_tax + rec.postage


    def _prepare_move_line1(self):
        move_line_dict = []
        amount = 0.0
        lc_commision_account = int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_amenmend_charge'))
        vat_account = int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_vat_account'))
        tax_account = int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_fund_taxes'))
        bank = int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_opening_bank'))
        bank_account = self.env['account.journal'].search([('id','=',bank)]).payment_credit_account_id.id

        move_line_dict.append({
            'account_id': lc_commision_account or False,
            'debit': (self.ammendment_charges + self.postage),
            # 'date_maturity': self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict.append({
            'account_id': vat_account or False,
            'debit': (self.foreign_vat + self.other_vat),
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict.append({
            'account_id': tax_account or False,
            'debit': self.source_tax,
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict.append({
            'account_id': bank_account or False,
            'credit': (self.ammendment_charges + self.postage + self.foreign_vat + self.other_vat + self.source_tax),
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })

        return move_line_dict

    def button_paid(self):
        move_lines1 = self._prepare_move_line1()
        vals = {
            'move_type': 'entry',
            'date': self.date_of_amendant,
            'journal_id': self.env['account.journal'].search([('name', '=', 'Miscellaneous Operations')], limit=1).id,
            'line_ids': [(0, 0, line_data) for line_data in move_lines1]
        }
        move_id1 = self.env['account.move'].create(vals)
        move_id1.ref = 'LC Ammendmend-'+ self.lc_no.lc_no

        self.write({'state' : 'paid'})



