# -*- coding: utf-8 -*-
from odoo import models, fields, api
from datetime import datetime


class CustomerBalanceWizard(models.TransientModel):
    _name = 'customer.balance.wizard'

    customer_id = fields.Many2one('res.partner', 'Customer')

    def get_report(self):
        today = fields.Date.today()
        customer_id = self.customer_id
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'customer_id': customer_id.name,
            },
        }
        return self.env.ref('customer_details_report.customer_balance_report').report_action(self, data=data)


class CustomerBalanceReport(models.AbstractModel):
    _name = 'report.customer_details_report.customer_balance_report_template'

    def percentage(self, part, whole):
        if whole:
            return "{:.1%}".format(float(part) / float(whole))
        return 0

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        customer_id = data['form']['customer_id']
        customer_name = self.env['res.partner'].browse(customer_id)

        customer_balance_dict = {}

        if customer_id:
            sales = self.env['sale.order'].search([('partner_id', '=', customer_id), ('state', '=', 'sale')])
            today = fields.Date.today()
            cut_off_date = today.replace(year=2021, month=6, day=30)
            journals = self.env['account.move.line'].search(
                [('partner_id', '=', customer_id), ('date', '<=', datetime.strftime(cut_off_date, "%Y-%m-%d"))])
            previous_balance = 0
            for line in journals:
                previous_balance = line.debit - line.credit
            customer_balance = 0.0

            for sale in sales:
                payments = self.env['account.payment'].search([('sale_id', '=', sale.id), ('state', '=', 'posted')])
                payment_amount = sum(payments.mapped('amount'))
                payment_date = payments.mapped('date')
                payment_bank = payments.mapped('journal_id.name')
                invoices = sale.invoice_ids.filtered(lambda x: x.state and x.state == 'posted')
                delivery_amount = sum(invoices.mapped('amount_total'))
                invoice_ref = invoices.mapped('name')
                pending_delivery_orders = sale.picking_ids.filtered(
                    lambda x: x.state == 'confirmed' or x.state == 'assigned')
                canceled_delivery_orders = sale.picking_ids.filtered(lambda x: x.state == 'cancel')
                pending_amount = 0.0
                for transfer in pending_delivery_orders:
                    for line in transfer.move_ids_without_package:
                        product_id = line.product_id.id
                        quantity = line.product_uom_qty
                        price_unit = line.sale_line_id.price_unit if line.sale_line_id else line.product_id.lst_price
                        discount = line.sale_line_id.discount
                        pending_amount += ((price_unit - (price_unit * discount) / 100) * quantity)

                cancel_do_amount = 0.0
                for transfer in canceled_delivery_orders:
                    for line in transfer.move_ids_without_package:
                        product_id = line.product_id.id
                        quantity = line.product_uom_qty
                        price_unit = line.sale_line_id.price_unit if line.sale_line_id else line.product_id.lst_price
                        discount = line.sale_line_id.discount
                        cancel_do_amount += ((price_unit - (price_unit * discount) / 100) * quantity)
                so_balance = payment_amount - delivery_amount - pending_amount
                customer_balance += so_balance
                customer_balance_dict.setdefault(customer_id, {'customer_code': sale.partner_id.code,
                                                               'customer_name': sale.partner_id.name,
                                                               'so_balance': so_balance,
                                                               'customer_balance': customer_balance
                                                               })
                customer_balance_dict.update({customer_id: {'customer_code': sale.partner_id.code,
                                                            'customer_name': sale.partner_id.name,
                                                            'so_balance': so_balance,
                                                            'customer_balance': customer_balance}})

        else:
            sales = self.env['sale.order'].search([('state', '=', 'sale')])
            customers = self.env['res.partner'].search([('is_customer', '=', True)])

            for customer in customers:
                today = fields.Date.today()
                cut_off_date = today.replace(year=2021, month=6, day=30)
                journals = self.env['account.move.line'].search(
                    [('partner_id.code', '=', customer.code),
                     ('date', '<=', datetime.strftime(cut_off_date, "%Y-%m-%d"))])
                previous_balance = 0
                for line in journals:
                    previous_balance = line.debit - line.credit
                customer_balance = 0.0
                so_balance = 0.0

                if (customer.sale_order_count == 0) and (previous_balance == 0):
                    continue

                for sale in sales:
                    if sale.partner_id == customer:
                        sale_amount = sale.amount_total
                        payments = self.env['account.payment'].search(
                            [('sale_id', '=', sale.id), ('state', '=', 'posted')])
                        payment_amount = sum(payments.mapped('amount'))
                        payment_date = payments.mapped('date')
                        payment_bank = payments.mapped('journal_id.name')
                        invoices = sale.invoice_ids.filtered(lambda x: x.state and x.state == 'posted')
                        delivery_amount = sum(invoices.mapped('amount_total'))
                        invoice_ref = invoices.mapped('name')
                        pending_delivery_orders = sale.picking_ids.filtered(
                            lambda x: x.state == 'confirmed' or x.state == 'assigned')
                        canceled_delivery_orders = sale.picking_ids.filtered(lambda x: x.state == 'cancel')
                        pending_amount = 0.0
                        for transfer in pending_delivery_orders:
                            for line in transfer.move_ids_without_package:
                                product_id = line.product_id.id
                                quantity = line.product_uom_qty
                                price_unit = line.sale_line_id.price_unit if line.sale_line_id else line.product_id.lst_price
                                discount = line.sale_line_id.discount
                                pending_amount += ((price_unit - (price_unit * discount) / 100) * quantity)

                        cancel_do_amount = 0.0
                        for transfer in canceled_delivery_orders:
                            for line in transfer.move_ids_without_package:
                                product_id = line.product_id.id
                                quantity = line.product_uom_qty
                                price_unit = line.sale_line_id.price_unit if line.sale_line_id else line.product_id.lst_price
                                discount = line.sale_line_id.discount
                                cancel_do_amount += ((price_unit - (price_unit * discount) / 100) * quantity)
                        so_balance = payment_amount - delivery_amount - pending_amount
                        customer_balance += so_balance
                        # customer_balance_dict.setdefault(customer_id, {'customer_code': sale.partner_id.code,
                        #                                                'customer_name': sale.partner_id.name,
                        #                                                'so_balance': so_balance,
                        #                                                'customer_balance': customer_balance
                        #                                                })

                customer_balance_dict.update({customer.code: {'customer_code': customer.code,
                                                              'customer_name': customer.name,
                                                              'so_balance': so_balance,
                                                              'customer_balance': customer_balance}})
        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'customer_id': customer_id,
            'customer_balance_dict': list(customer_balance_dict.values()),
            'customer_balance': customer_balance,
            'previous_balance': abs(previous_balance)
        }
