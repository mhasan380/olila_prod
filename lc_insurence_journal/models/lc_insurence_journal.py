# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime

class Insurance(models.Model):
    _inherit = "insurance.cover"


    def action_open_picking_invoice(self):
        """This is the function of the smart button which redirect to the invoice related to the current picking"""
        name = 'Bills'
        return {
            'name': name,
            'type': 'ir.actions.act_window',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('lc_insurence_id', '=', self.id)],
            'context': {'create': False},
            'target': 'current'
        }


    def create_invoice(self, type='in_invoice', invoice_amount=None, currency_id=None, partner_id=None, date_invoice=None):
        date_invoice = self.insurence_date
        product = self.env['product.product'].search([('name','=','Marine Insurance Premium')],limit=1)

        invoice_vals = {
            'currency_id':currency_id.id,
            'move_type': type,
            'partner_id': self.partner_id.id,
            'invoice_date': date_invoice,
            'date': date_invoice,
            'lc_insurence_id': self.id,
            'ref' : self.insurance_cover_no,
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
        if self.insurance_cover_no:
            invoice_record = self.create_invoice(type='in_invoice', invoice_amount=self.premium_amount, currency_id=self.currency_id)
            # import pdb;pdb.set_trace();
            # self.invoice_id = invoice_record.id
            self.write({'state' : 'confirm'})
        else:
            raise UserError(_('Please Input Marine Cover Note Number.'))

        return True

    invoice_count = fields.Integer(string='Invoices', compute='_compute_invoice_count')
    def _compute_invoice_count(self):
        move_ids = self.env['account.move'].sudo().search([('lc_insurence_id', '=', self.id)])
        self.invoice_count = len(move_ids)


