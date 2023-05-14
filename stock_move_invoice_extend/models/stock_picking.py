# -*- coding: utf-8 -*-
import operator as py_operator
from odoo import fields, models, _
from odoo.exceptions import UserError
from datetime import datetime, timedelta

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}

class StockPicking(models.Model):
    _inherit = 'stock.picking'


    def _compute_invoice_count(self):
        """This compute function used to count the number of invoice for the picking"""
        for picking_id in self:
            move_ids = picking_id.env['account.move'].sudo().search([('invoice_origin', '=', picking_id.name)])
            if move_ids:
                picking_id.invoice_count = len(move_ids)
            else:
                picking_id.invoice_count = 0



    def create_customer_credit(self):
        """This is the function for creating customer credit note
                from the picking"""
        for picking_id in self:
            customer_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param('stock_move_invoice.customer_journal_id') or False
            if not customer_journal_id:
                raise UserError(_("Please configure the journal from account settings"))
            invoice_line_list = []
            for move in picking_id.move_ids_without_package:
                account = move.product_id.property_account_income_id.id if move.product_id.property_account_income_id else move.product_id.categ_id.property_account_income_categ_id.id
                vals = (0, 0, {
                    'name': move.description_picking,
                    'product_id': move.product_id and move.product_id.id,
                    'price_unit': move.sale_line_id.price_unit if move.sale_line_id else move.product_id.lst_price,
                    'sale_line_ids': move.sale_line_id and [(6, 0, [move.sale_line_id.id])] or False,
                    'account_id': account,
                    'discount': move.sale_line_id.discount,
                    'tax_ids': [(6, 0, move.sale_line_id.tax_id.ids)],
                    'quantity': move.quantity_done,
                })
                invoice_line_list.append(vals)
            if picking_id.invoice_count == 0:
                invoice = picking_id.env['account.move'].sudo().create({
                    'move_type': 'out_refund',
                    'invoice_origin': picking_id.name,
                    'invoice_user_id': self.env.uid,
                    'narration': picking_id.name,
                    'partner_id': picking_id.partner_id and picking_id.partner_id.id,
                    'currency_id': picking_id.sale_id.currency_id.id if picking_id.sale_id else picking_id.company_id.currency_id.id,
                    'journal_id': int(customer_journal_id),
                    'payment_reference': picking_id.name,
                    'picking_id': picking_id.id,
                    'invoice_line_ids': invoice_line_list,
                    'invoice_date' : picking_id.scheduled_date.date()
                })
            return invoice

    def create_invoice(self):
        for picking_id in self:
            customer_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param(
                'stock_move_invoice.customer_journal_id') or False
            if not customer_journal_id:
                raise UserError(_("Please configure journal from account settings"))
            invoice_line_list = []
            for move in picking_id.move_ids_without_package:
                account = move.product_id.property_account_income_id if move.product_id.property_account_income_id else move.product_id.categ_id.property_account_income_categ_id
                vals = (0, 0, {
                    'name': move.description_picking,
                    'product_id': move.product_id.id,
                    'quantity': move.quantity_done,
                    'price_unit': move.sale_line_id.price_unit if move.sale_line_id else move.product_id.lst_price,
                    'sale_line_ids': move.sale_line_id and [(6, 0, [move.sale_line_id.id])] or False,
                    'account_id': account and account.id,
                    'discount': move.sale_line_id.discount,
                    'tax_ids': [(6, 0, move.sale_line_id.tax_id.ids)],
                })
                invoice_line_list.append(vals)
            invoice = picking_id.env['account.move'].sudo().create({
                'move_type': 'out_invoice',
                'invoice_origin': picking_id.name,
                'invoice_user_id': self.env.uid,
                'narration': picking_id.name,
                'partner_id': picking_id.partner_id and picking_id.partner_id.id,
                'currency_id': picking_id.sale_id.currency_id.id if picking_id.sale_id else picking_id.company_id.currency_id.id,
                'journal_id': int(customer_journal_id),
                'payment_reference': picking_id.name,
                'picking_id': picking_id.id,
                'invoice_date': picking_id.scheduled_date,
                'invoice_line_ids': invoice_line_list
            })
            return invoice

    def _bill_invoice_line(self, move):
        account = move.product_id.property_account_expense_id if move.product_id.property_account_expense_id else move.product_id.categ_id.property_account_expense_categ_id
        factor = move.purchase_line_id.product_uom.factor_inv
        return {
            'name': move.description_picking,
            'product_id': move.product_id.id,
            'price_unit':  move.purchase_line_id.price_unit if move.purchase_line_id else move.product_id.standard_price,
            'account_id': account and account.id,
            'tax_ids': [(6, 0, move.purchase_line_id.taxes_id.ids)],
            'discount' : move.purchase_line_id.discount if move.purchase_line_id else 0.0,
            'quantity': (move.quantity_done / factor),
            'purchase_line_id': move.purchase_line_id and move.purchase_line_id.id or False,
            'product_uom_id' : move.purchase_line_id.product_uom.id
        }

    def create_bill(self):
        for picking_id in self:
            vendor_journal_id = picking_id.env['ir.config_parameter'].sudo().get_param('stock_move_invoice.vendor_journal_id') or False
            if not vendor_journal_id:
                raise UserError(_("Please configure the journal from account settings."))
            invoice_lines = [(0, 0, self._bill_invoice_line(move)) for move in picking_id.move_ids_without_package]
            partner_id = picking_id.purchase_id and picking_id.purchase_id.partner_id
            invoice = picking_id.env['account.move'].create({
                'move_type': 'in_invoice',
                'partner_id' : partner_id and partner_id,
                'invoice_origin': picking_id.name,
                'invoice_user_id': self.env.uid,
                'narration': picking_id.name,
                'journal_id': int(vendor_journal_id),
                'payment_reference': picking_id.name,
                'picking_id': picking_id.id,
                'currency_id' : picking_id.purchase_id.currency_id.id if picking_id.purchase_id else picking_id.company_id.currency_id.id,
                'invoice_date': picking_id.scheduled_date,
                'invoice_line_ids': invoice_lines
            })
            return invoice



