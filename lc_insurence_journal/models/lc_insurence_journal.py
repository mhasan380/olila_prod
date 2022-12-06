# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class Insurance(models.Model):
    _inherit = "insurance.cover"


    def create_invoice(self, type='in_invoice', invoice_amount=None, currency_id=None, partner_id=None, date_invoice=None):
        date_invoice = self.insurence_date
        product = self.env['product.product'].search([('name','=','Marine Insurance Premium')],limit=1)

        invoice_vals = {
            'currency_id':currency_id.id,
            'move_type': type,
            'partner_id': self.partner_id.id,
            'invoice_date': date_invoice,
            'date': date_invoice,
            'invoice_line_ids': [(0, 0, {
                'product_id': product.id,
                'name': 'Insurance Premium',
                'quantity': 1,
                'price_unit': invoice_amount,
                'tax_ids': [(6, 0, [])],
            })]
        }
        invoice = self.env['account.move'].with_context(default_move_type=type).create(invoice_vals)
        return invoice

    def button_confirm(self):
        invoice_record = self.create_invoice(type='in_invoice', invoice_amount=self.premium_amount, currency_id=self.currency_id)
        # import pdb;pdb.set_trace();
        # self.invoice_id = invoice_record.id
        self.write({'state' : 'confirm'})
        return True

