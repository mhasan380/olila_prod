# -*- coding: utf-8 -*-
from odoo import _, fields, http, release
from odoo.http import request, Response
from odoo.models import check_method_name
from odoo.tools.image import image_data_uri
from odoo.tools import misc, config
from odoo.exceptions import ValidationError, UserError
from werkzeug import secure_filename, exceptions
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone
from odoo.addons.dsl_employee_access import tools
from odoo.addons.dsl_employee_access.tools.json import ResponseEncoder
import string
from secrets import choice
import random

import base64
import json
import re
import urllib

_csrf = config.get('rest_csrf', False)
import logging

_logger = logging.getLogger(__name__)


class EmployeeTargetAchievement(http.Controller):

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/payment/data', auth='none', type='http', csrf=False, methods=['POST'])
    def get_payment_data(self, **kwargs):
        try:
            # _logger.warning(f' ============== ' + str(kwargs['empl']) + ' -- ' + str(kwargs['unauthorize']))
            # employee = request.env['hr.employee'].sudo().search([('id', '=', kwargs['empl'])])
            # payment_journals = request.env['account.journal'].sudo().search([('type', 'in', ['bank', 'cash'])])
            payment_journals = request.env['account.journal'].sudo().search([('type', '=', 'bank')])

            order = request.env['sale.order'].sudo().search([('id', '=', kwargs['order_id'])])
            res_dict = {}
            res_dict['customer_id'] = order.partner_id.id
            res_dict['customer_name'] = order.partner_id.name
            res_dict['amount_total'] = order.amount_total
            res_dict['balance'] = self.get_customer_balance(order.partner_id.id)
            res_dict['customer_address'] = order.address
            res_dict['customer_code'] = order.partner_id.code

            journals = []
            for journal in payment_journals:
                journal_dict = {}
                journal_dict['id'] = journal.id
                journal_dict['name'] = journal.name
                journal_dict['type'] = journal.type
                accounts = []
                if journal.type == 'bank':
                    banks_accounts = request.env['res.partner.bank'].sudo().search([('journal_id', '=', journal.id)])
                    account_dict = {}
                    for acc in banks_accounts:
                        account_dict['id'] = acc.id
                        account_dict['acc_number'] = acc.acc_number
                        accounts.append(account_dict)
                journal_dict['accounts'] = accounts
                journals.append(journal_dict)

            res_dict['journals'] = journals

            payments = []
            for advance_payment in order.sale_payment_ids:
                payment_dict = {}
                payment_dict['id'] = advance_payment.id
                payment_dict['number'] = advance_payment.name
                payment_dict['date'] = advance_payment.date
                payment_dict['method'] = advance_payment.journal_id.name
                payment_dict['amount'] = advance_payment.amount
                payment_dict['status'] = advance_payment.state
                payment_dict['customer'] = advance_payment.partner_id.name
                payments.append(payment_dict)

            res_dict['payments'] = payments
            res_dict['payment_count'] = order.payment_count

            msg = json.dumps(res_dict,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_p_01',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/payment/collections', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_my_payment_collections(self, **kwargs):
        try:
            start_date = datetime.strptime(kwargs["start_date"], '%Y-%m-%d')
            end_date = datetime.strptime(kwargs["end_date"], '%Y-%m-%d')
            modified_end_date = end_date + timedelta(days=1)

            including_subordinates = []
            employee = request.env['hr.employee'].sudo().browse(request.em_id)
            including_subordinates.append(employee)
            including_subordinates.extend(self.get_subordinates(employee))
            accessible_ids = []
            for sub in including_subordinates:
                accessible_ids.append(sub.id)
            payment_ids = request.env['account.payment'].sudo().search(
                [('payment_type', '=', 'inbound'), ('responsible_id', 'in', accessible_ids)], order='id desc')

            payment_collection = []
            for payment in payment_ids:
                if start_date.date() <= payment.date < modified_end_date.date():
                    payment_dict = {}
                    payment_dict['id'] = payment.id
                    payment_dict['number'] = payment.name
                    payment_dict['so'] = payment.sale_id.name
                    payment_dict['date'] = payment.date
                    payment_dict['method'] = payment.journal_id.name
                    payment_dict['amount'] = payment.amount
                    payment_dict['status'] = payment.state
                    payment_dict['responsible'] = payment.responsible_id.name
                    payment_dict['responsible_id'] = payment.responsible_id.id
                    payment_dict['customer'] = payment.partner_id.name
                    payment_collection.append(payment_dict)

            msg = json.dumps(payment_collection,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_p_02',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/payment/collect', auth='none', type='http', csrf=False, methods=['POST'])
    def payment_collect(self, **kwargs):
        try:
            # _logger.warning(f' ============== ' + str(kwargs['empl']) + ' -- ' + str(kwargs['unauthorize']))
            # employee = request.env['hr.employee'].sudo().search([('id', '=', kwargs['empl'])])
            # payment_journals = request.env['account.journal'].sudo().search([('type', 'in', ['bank', 'cash'])])
            employee = request.env['hr.employee'].sudo().browse(request.em_id)
            journal_id = request.env['account.journal'].sudo().browse(int(kwargs['method_id']))
            amount = float(kwargs['amount'])
            payment_date = kwargs['payment_date']
            if kwargs['account_id']:
                account_id = request.env['res.partner.bank'].sudo().browse(int(kwargs['account_id'])).id
            else:
                account_id = False
            cheque_number = kwargs['cheque_number']
            if kwargs['cheque_date']:
                cheque_date = kwargs['cheque_date']
            else:
                cheque_date = False
            branch = kwargs['branch']
            # responsible = employee.id

            sale_id = kwargs['order_id']
            # _logger.warning(f'------------------{sale_id}')
            if sale_id:
                sale = request.env['sale.order'].sudo().browse(int(sale_id))
                _logger.warning(f'------------------{sale.name}')
                exchange_rate = request.env['res.currency'].sudo()._get_conversion_rate(sale.company_id.currency_id,
                                                                                        sale.currency_id,
                                                                                        sale.company_id,
                                                                                        sale.date_order)
                currency_amount = amount * (1.0 / exchange_rate)
                payment_dict = {'payment_type': 'inbound',
                                'partner_type': 'customer',
                                'sale_id': sale.id,
                                'responsible_id': sale.responsible and sale.responsible.id,
                                #'responsible_id': employee and employee.id,
                                'ref': _("Advance") + " - " + sale.name,
                                'partner_id': sale.partner_id and sale.partner_id.id,
                                'journal_id': journal_id and journal_id.id,
                                'company_id': sale.company_id and sale.company_id.id,
                                'currency_id': sale.pricelist_id.currency_id and sale.pricelist_id.currency_id.id,
                                'date': payment_date,
                                'amount': currency_amount,
                                'check_no': cheque_number,
                                'check_date': cheque_date,
                                'payment_method_id': request.env.ref('account.account_payment_method_manual_in').id,
                                'partner_bank_id': account_id,
                                'customer_code': sale.partner_id.code,
                                'bank_branch': branch,
                                # 'file_attachment': false,
                                }
                payment = request.env['account.payment'].sudo().create(payment_dict)
                if payment.id:
                    created = True
                    value = 'Successfully Submitted'
                else:
                    created = False
                    value = 'Failed to Submitted. Please contact to administrator'
            else:
                created = False
                value = 'You can not collect payment for this sale order'
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='fun_p_01',
                                                 trace_ref='excepted_payment_collect', with_location=True)
            msg = json.dumps({'result': created, 'data': value},
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_p_03',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    def get_customer_balance(self, customer_id):
        try:
            # customer_id = request.env['res.partner'].sudo().browse(cus_id).id
            sales = request.env['sale.order'].sudo().search([('partner_id', '=', customer_id), ('state', '=', 'sale')])
            customer_balance = 0.0
            for sale in sales:
                payments = request.env['account.payment'].sudo().search(
                    [('sale_id', '=', sale.id), ('state', '=', 'posted')])
                payment_amount = sum(payments.mapped('amount'))
                invoices = sale.invoice_ids.filtered(lambda x: x.state and x.state == 'posted')
                delivery_amount = sum(invoices.mapped('amount_total'))
                pending_delivery_orders = sale.picking_ids.filtered(
                    lambda x: x.state == 'confirmed' or x.state == 'assigned')
                pending_amount = 0.0
                for transfer in pending_delivery_orders:
                    for line in transfer.move_ids_without_package:
                        product_id = line.product_id.id
                        quantity = line.product_uom_qty
                        price_unit = line.sale_line_id.price_unit if line.sale_line_id else line.product_id.lst_price
                        discount = line.sale_line_id.discount
                        pending_amount += ((price_unit - (price_unit * discount) / 100) * quantity)
                so_balance = payment_amount - delivery_amount - pending_amount
                customer_balance += so_balance

            return customer_balance
        except Exception as e:
            return -999999

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/payment/update', auth='none', type='http', csrf=False, methods=['POST'])
    def payment_update_amount(self, **kwargs):
        try:
            amount = float(kwargs['amount'])
            vals = {
                'amount': amount
            }
            payment_id = request.env['account.payment'].sudo().search([('id', '=', kwargs['id'])])

            # if payment_id.responsible_id.id == request.em_id:
            if payment_id.state == 'draft':
                bol = payment_id.write(vals)
                value = 'Payment amount successfully updated'
            else:
                bol = False
                value = 'This payment is not in Draft state'
            # else:
            #     bol = False
            #     value = 'You are not allowed to update this payment'

            msg = json.dumps({'result': bol, 'data': value},
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_p_04',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    def get_subordinates(self, employee):
        subordinate_list = []
        subordinates = request.env['hr.employee'].sudo().search(
            [('parent_id', '=', employee.id), '|', ('active', '=', True), ('active', '=', False)])
        subordinate_list.extend(subordinates)
        for subordinate in subordinates:
            subordinate_list.extend(self.get_subordinates(subordinate))

        return subordinate_list
