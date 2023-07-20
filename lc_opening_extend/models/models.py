# -*- coding: utf-8 -*-

from odoo import models, fields, api

class LcOpening(models.Model):
    _inherit ="lc.opening"

    def button_accept(self):
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
            rec.write({'state': 'accept'})

    state = fields.Selection(
        [('draft', 'Draft'), ('confirm', 'Confirm'), ('accept', 'Accept'), ('amendment', 'Amendment'), ('done','Done'),
         ('cancel', 'Cancel')],
        string='Status', readonly=True, index=True, copy=False, default='draft', tracking=True)

    def close_lc(self):
        for rec in self:
            rec.state = 'done'





