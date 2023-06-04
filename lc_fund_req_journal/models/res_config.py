# -*- coding: utf-8 -*-
from odoo import fields, models, api


class Settings(models.TransientModel):
    _inherit = 'res.config.settings'

    lc_opening_bank = fields.Many2one('account.journal', string="LC Opening Bank")
    lc_margin_account = fields.Many2one('account.account', string="LC Margin Account")
    lc_com_account = fields.Many2one('account.account', string="LC Comission Account")
    lc_fund_taxes = fields.Many2one('account.account', string="LC TAX Account")
    lc_lcfr_other_charges = fields.Many2one('account.account', string="LC Other Charges Account")
    lc_vat_account = fields.Many2one('account.account', string="LC VAT Account")
    lc_amenmend_charge = fields.Many2one('account.account', string="LC Amendmend Account")
    ltr_account = fields.Many2one('account.account', string="LTR Account")
    transit_account = fields.Many2one('account.account', string="Stock Transit Account")
    bank_charges = fields.Many2one('account.account', string="Bank Charges Account")
    interest_account = fields.Many2one('account.account', string="Interest Account")

    @api.model
    def get_values(self):
        res = super(Settings, self).get_values()
        res.update(
            lc_opening_bank= int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_opening_bank')),
            lc_margin_account= int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_margin_account')),
            lc_com_account= int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_com_account')),
            lc_fund_taxes= int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_fund_taxes')),
            lc_lcfr_other_charges= int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_lcfr_other_charges')),
            lc_vat_account= int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_vat_account')),
            lc_amenmend_charge= int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.lc_amenmend_charge')),
            ltr_account= int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.ltr_account')),
            transit_account=int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.transit_account')),
            bank_charges=int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.bank_charges')),
            interest_account=int(self.env['ir.config_parameter'].sudo().get_param(
                'lc_fund_req_journal.interest_account')),
        )
        return res

    def set_values(self):
        res= super(Settings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()

        lc_opening_bank = self.lc_opening_bank and self.lc_opening_bank.id or False
        lc_margin_account = self.lc_margin_account and self.lc_margin_account.id or False
        lc_com_account = self.lc_com_account and self.lc_com_account.id or False
        lc_fund_taxes = self.lc_fund_taxes and self.lc_fund_taxes.id or False
        lc_lcfr_other_charges = self.lc_lcfr_other_charges and self.lc_lcfr_other_charges.id or False
        lc_vat_account = self.lc_vat_account and self.lc_vat_account.id or False
        lc_amenmend_charge = self.lc_amenmend_charge and self.lc_amenmend_charge.id or False
        ltr_account = self.ltr_account and self.ltr_account.id or False
        transit_account = self.transit_account and self.transit_account.id or False
        bank_charges = self.bank_charges and self.bank_charges.id or False
        interest_account = self.interest_account and self.interest_account.id or False

        param.set_param('lc_fund_req_journal.lc_opening_bank', lc_opening_bank)
        param.set_param('lc_fund_req_journal.lc_margin_account', lc_margin_account)
        param.set_param('lc_fund_req_journal.lc_com_account', lc_com_account)
        param.set_param('lc_fund_req_journal.lc_fund_taxes', lc_fund_taxes)
        param.set_param('lc_fund_req_journal.lc_lcfr_other_charges', lc_lcfr_other_charges)
        param.set_param('lc_fund_req_journal.lc_vat_account', lc_vat_account)
        param.set_param('lc_fund_req_journal.lc_amenmend_charge', lc_amenmend_charge)
        param.set_param('lc_fund_req_journal.ltr_account', ltr_account)
        param.set_param('lc_fund_req_journal.transit_account', transit_account)
        param.set_param('lc_fund_req_journal.bank_charges', bank_charges)
        param.set_param('lc_fund_req_journal.interest_account', interest_account)

        return res
