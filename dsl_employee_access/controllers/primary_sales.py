# -*- coding: utf-8 -*-
from odoo import _, fields, http, release
from odoo.http import request, Response
from odoo.models import check_method_name
from odoo.tools.image import image_data_uri
from odoo.tools import misc, config
from odoo.exceptions import ValidationError, UserError
from werkzeug import secure_filename, exceptions
from datetime import date, datetime, time
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


class PrimarySales(http.Controller):

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/sale_order/my', website=True, auth='none', type='http', csrf=False, methods=['GET'])
    def get_employee_all_sales(self, **kwargs):
        try:
            start_date = datetime.strptime(kwargs["start_date"], '%Y-%m-%d')
            end_date = datetime.strptime(kwargs["end_date"], '%Y-%m-%d')

            # _logger.warning(f' ============== ' + str(start_date) + ' -- ' + str(end_date))
            # _logger.warning(f' ============== ' + str(kwargs['empl']) + ' -- ' + str(kwargs['unauthorize']))
            my_sale_orders = request.env['sale.order'].sudo().search([('responsible.id', '=', kwargs['empl'])])
            _logger.warning(f' ============== ' + str(len(my_sale_orders)))
            my_orders = []
            for order in my_sale_orders:
                if start_date <= order.date_order < end_date:
                    # dt_obj = datetime.strptime(order.date_order,'%Y-%m-%d')
                    millisec = order.date_order.timestamp() * 1000
                    sale_dict = {'id': order.id, 'name': order.name, 'total': order.amount_total, 'sate': order.state,
                                 'customer': order.partner_id.name, 'date': order.date_order,
                                 'date_long': int(millisec)}
                    my_orders.append(sale_dict)

            msg = json.dumps(my_orders,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/sale_order/info', auth='none', type='http', csrf=False, methods=['POST'])
    def get_sale_info(self, **kwargs):
        try:
            order = request.env['sale.order'].sudo().search([('id', '=', kwargs['id'])])
            order_lines = []
            for line in order.order_line:
                order_line = {'id': line.product_id.id,
                              'name': line.product_id.name,
                              'product_uom_qty': line.product_uom_qty,
                              'price_unit': line.price_unit,
                              'price_subtotal': line.price_subtotal,
                              }
                order_lines.append(order_line)

            order_details = {
                'name': order.name,
                'customer': order.partner_id.name,
                # 'customer_address': order.partner_id.street,
                'customer_address': order.address,
                # 'customer_mobile': order.partner_id.mobile,
                'customer_mobile': order.contact_no,
                'balance': self.get_customer_balance(order.partner_id.id),
                'zone': order.zone_id.name,
                'state': order.state,
                'amount_total': order.amount_total,
                'amount_untaxed': order.amount_untaxed,
                'total_discount': order.total_discount,
                'secondary_contact': order.secondary_contact_persion,
                'warehouse': order.warehouse_id.name,
                'date_order': order.date_order,
                'order_lines': order_lines
            }

            msg = json.dumps(order_details,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/sale_order/my_customers', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_my_customers(self, **kwargs):
        try:

            me = request.env['hr.employee'].sudo().browse(request.em_id)
            customers = request.env['res.partner'].sudo().search([('responsible', '=', me.id)])
            # customers = request.env['res.partner'].sudo().search([('responsible', '=', me.id)])

            records = []
            for customer in customers:
                customer_dict = {'id': customer.id,
                                 'name': customer.name,
                                 'price_list_id': customer.with_context(
                                     allowed_company_ids=[1]).property_product_pricelist.id,
                                 'price_list': customer.with_context(
                                     allowed_company_ids=[1]).property_product_pricelist.name,
                                 'payment_id': customer.with_context(
                                     allowed_company_ids=[1]).property_payment_term_id.id,
                                 'payment': customer.with_context(
                                     allowed_company_ids=[1]).property_payment_term_id.name,
                                 'warehouse_id': customer.deport_warehouse_id.id,
                                 'warehouse': customer.deport_warehouse_id.name,
                                 'contact_no': customer.mobile,
                                 'address': customer.street,
                                 'balance': self.get_customer_balance(customer.id),
                                 'secondary_contact': customer.secondary_contact_persion,
                                 'zone_id': customer.zone_id.id,
                                 'zone': customer.zone_id.name,
                                 'discount': customer.discount,
                                 'code': customer.code}
                records.append(customer_dict)

            msg = json.dumps(records,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/sale_order/products', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_products_for_sale(self, **kwargs):
        try:

            products = request.env['product.product'].sudo().search(
                [('sale_ok', '=', True), ('purchase_ok', '=', True), ('type', '=', 'product'),
                 ('default_code', '!=', False)], order='id desc')

            product_records = []
            for product in products:
                product_dict = {'id': product.id,
                                'name': product.name,
                                'price': product.list_price,
                                'available': product.virtual_available,
                                'code': product.default_code
                                }
                product_records.append(product_dict)

            msg = json.dumps(product_records,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/sale_order/create', auth='none', type='http', csrf=False, methods=['POST'])
    def create_order(self, **kwargs):
        try:
            data = request.httprequest.data
            data_in_json = json.loads(data)
            _logger.warning(f' ----- - {data_in_json}')

            customer = request.env['res.partner'].sudo().search([('id', '=', data_in_json['customer_id'])])

            order_lines = []
            for product_data in data_in_json['products']:
                product = request.env['product.product'].sudo().search([('id', '=', product_data['id'])])
                order_line_dict = {
                    'product_id': product.id,
                    'shipping_partner_id': customer.id,
                    'warehouse_id': customer.deport_warehouse_id.id,
                    'name': product.name,
                    'product_uom_qty': product_data['quantity'],
                    'price_unit': product.lst_price,
                    'discount': customer.discount
                }
                order_lines.append((0, 0, order_line_dict))

            order_vals = {
                'partner_id': customer.id,
                'partner_invoice_id': customer.id,
                'partner_shipping_id': customer.id,
                'contact_no': customer.mobile,
                'address': customer.street,
                'date_order': datetime.now(),
                'payment_term_id': customer.with_context(
                    allowed_company_ids=[1]).property_payment_term_id.id,
                'pricelist_id': customer.with_context(
                    allowed_company_ids=[1]).property_product_pricelist.id,
                'dealer_code': customer.code,
                'secondary_contact_persion': customer.secondary_contact_persion,
                'zone_id': customer.zone_id.id,
                'sale_type': 'primary_sales',
                'responsible': request.em_id,
                'team_id': customer.team_id.id,
                'require_signature': True,
                'warehouse_id': customer.deport_warehouse_id.id,
                'state': 'draft',
                'company_id': 1,
                'order_line': order_lines
            }

            order_id = request.env['sale.order'].sudo().create(order_vals)

            order_details = {
                'id': order_id.id,
                'name': order_id.name
            }
            msg = json.dumps(order_details,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/sale_order/delete', auth='none', type='http', csrf=False, methods=['POST'])
    def delete_sale_order(self, **kwargs):
        try:
            order = request.env['sale.order'].sudo().search([('id', '=', kwargs['id'])])
            if order.state == 'draft':
                value = f'The order number {order.name} has been deleted successfully'
                bol = order.unlink()
            else:
                bol = False
                value = 'This order is not in Quotation state'

            msg = json.dumps({'result': bol, 'data': value},
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/sale_order/confirm', auth='none', type='http', csrf=False, methods=['POST'])
    def confirm_sale_order(self, **kwargs):
        try:
            vals = {
                'state': 'waiting_for_approval'
            }
            order = request.env['sale.order'].sudo().search([('id', '=', kwargs['id'])])
            if order.state == 'draft':
                bol = order.write(vals)
                value = 'Now the order is waiting for approval.'
            else:
                bol = False
                value = 'This order is not in Quotation state'

            msg = json.dumps({'result': bol, 'data': value},
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    # @http.route('/web/test1', website=True, auth='none', type='http', csrf=False, methods=['GET'])
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
