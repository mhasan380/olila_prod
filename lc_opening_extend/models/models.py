# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LcOpening(models.Model):
    _inherit ="lc.opening"

    def _prepare_move_line1(self):

        move_line_dict = []
        bank = int(self.env['ir.config_parameter'].sudo().get_param(
            'lc_fund_req_journal.lc_opening_bank'))
        bank_account = self.env['account.journal'].search([('id', '=', bank)]).payment_credit_account_id.id
        lc_margin_account = int(self.env['ir.config_parameter'].sudo().get_param(
            'lc_fund_req_journal.lc_margin_account'))
        move_line_dict.append({
            'account_id': bank_account,
            'credit': self.requisition_id.margin,
            'name': 'LC No: ' + str(self.lc_no),
            # 'date_maturity': self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict.append({
            'account_id': lc_margin_account or False,
            'debit': self.requisition_id.margin,
            'name': 'LC No: ' + str(self.lc_no),
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })

        return move_line_dict

    def _prepare_move_line2(self):
        move_line_dict2 = []
        vat_account = int(self.env['ir.config_parameter'].sudo().get_param(
            'lc_fund_req_journal.lc_vat_account'))
        tax_account = int(self.env['ir.config_parameter'].sudo().get_param(
            'lc_fund_req_journal.lc_fund_taxes'))
        lc_outher_charges = int(self.env['ir.config_parameter'].sudo().get_param(
            'lc_fund_req_journal.lc_lcfr_other_charges'))
        lc_com_account = int(self.env['ir.config_parameter'].sudo().get_param(
            'lc_fund_req_journal.lc_com_account'))
        bank = int(self.env['ir.config_parameter'].sudo().get_param(
            'lc_fund_req_journal.lc_opening_bank'))
        bank_account = self.env['account.journal'].search([('id', '=', bank)]).payment_credit_account_id.id
        move_line_dict2.append({
            'account_id': bank_account or False,
            'credit': (self.requisition_id.commission + self.requisition_id.source_tax + self.requisition_id.vat_on_commission
                        + self.requisition_id.pt_charge + self.requisition_id.other_charges),
            # 'date_maturity': self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict2.append({
            'account_id': lc_com_account or False,
            'debit': self.requisition_id.commission,
            'name': 'Comission'
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict2.append({
            'account_id': tax_account or False,
            'debit': self.requisition_id.source_tax,
            'name': 'Source Tax'
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict2.append({
            'account_id': vat_account or False,
            'debit': self.requisition_id.vat_on_commission,
            'name': 'VAT on Comission'
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })
        move_line_dict2.append({
            'account_id': lc_outher_charges or False,
            'debit': (self.requisition_id.pt_charge + self.requisition_id.other_charges),
            'name': 'PT and Other Charges'
            # 'date_maturity' : self.move_date,
            # 'date' : self.move_date,
        })
        return move_line_dict2

    def button_accept(self):
        bank = int(self.env['ir.config_parameter'].sudo().get_param(
            'lc_fund_req_journal.lc_opening_bank'))
        for rec in self:
            lc_prayer = self.env['lc.request'].search([('requisition_id', '=', rec.requisition_id.id)])
            bills = self.env['account.move'].search([('invoice_origin', '=', rec.order_id.name)])
            total_amount = 0
            for bill in bills:
                if bill.state == 'posted':
                    total_amount = total_amount + bill.amount_total_signed * (-1)

            doc_releases = self.env['document.release.letter'].search([('lc_open_id', '=', rec.id)])
            doc_list =[]
            for doc in doc_releases:
                if doc.commercial_number:
                    doc_list.append(doc.commercial_number)
            separator = ', '
            comc = str(separator.join(doc_list))
            vals = {
                 'lc_number' : rec.id,
                 'lc_no' : rec.lc_no,
                 'lc_expiry_date' : rec.expire_date,
                 'country_id' : rec.origin.id,
                  'port_of_landing' : rec.port_of_landing,
                  'lc_open_date' : rec.lc_date,
                'opening_bank' : lc_prayer.lc_opening_bank,
                    'lc_type' : lc_prayer.lc_type,
                    'partner_id' : rec.order_id.partner_id.id,
                    'lc_value_usd' : rec.lc_amount,
                    'proforma' : rec.order_id.partner_ref,
                    'insurance' : self.env['insurance.cover'].search([('lc_requisition_id', '=', rec.requisition_id.id)]).id,
                    'partial_shipment' : total_amount,
                    'commercial' : comc,
                    'ex_rate' : rec.requisition_id.conversion_rate

            }

            lc_register = self.env['lc.register'].create(vals)
            lc_register_lines = self.env['lc.register.lines']

            for line in rec.lc_opening_lines:
                line_data = { 'lc_register_id': lc_register.id,
                              'product_id': line.product_id.id, 'quantity': line.quantity,
                                                 'item_code': line.item_code,
                                                 'unit_price': line.unit_price,
                                                  }
                lc_register_lines.create(line_data)
            lc_register.onchange_exchange()
            lc_register.onchange_partial()
            if rec.requisition_id:
                rec.requisition_id.state = 'accept'
            ##Journal Entry
            move_lines1 = rec._prepare_move_line1()
            vals = {
                'move_type': 'entry',
                'date': rec.lc_date,
                'journal_id': self.env['account.journal'].search([('id','=', bank)], limit=1).id,
                 'opening_id' : self.id,
                'line_ids': [(0, 0, line_data) for line_data in move_lines1]
            }
            move_id1 = self.env['account.move'].create(vals)
            move_id1.ref = 'LC Margin for ' + rec.lc_no

            move_lines2 = rec._prepare_move_line2()
            vals2 = {
                'move_type': 'entry',
                'date':  rec.lc_date,
                'journal_id': self.env['account.journal'].search([('id', '=', bank)], limit=1).id,
                'opening_id': self.id,
                'line_ids': [(0, 0, line_data) for line_data in move_lines2]
            }
            move_id2 = self.env['account.move'].create(vals2)
            move_id2.ref = 'LC Comission and Other Charges for ' + rec.lc_no
            rec.write({'state': 'accept'})

    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('accept', 'Accept'), ('amendment', 'Amendment'), ('done','Done'),
         ('cancel', 'Cancel')],
        string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def close_lc(self):
        for rec in self:
            rec.state = 'done'





