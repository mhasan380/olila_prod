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
import pytz
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


class SecondaryCustomer(http.Controller):

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/order/pre_create', auth='none', type='http', csrf=False, methods=['POST'])
    def get_secondary_sale_order_pre_create_data(self, **kwargs):
        try:
            distributor = request.env['res.partner'].sudo().search([('id', '=', kwargs['distributor'])])

            rec_dict = {}
            if distributor:
                stock = request.env['primary.customer.stocks'].sudo().search([('customer_id', '=', distributor.id)])
                if stock:
                    stock_products = []
                    for stock_line in stock.customer_stocks:
                        raw_code = stock_line.product_id.default_code
                        if raw_code and '/' in raw_code:
                            x = raw_code.split('/')[1:]
                            raw_code = x[0]
                        stocks_dict = {
                            'product_id': stock_line.product_id.id,
                            'product_name': stock_line.product_id.name,
                            'current_stock': stock_line.current_stock,
                            'sale_price': stock_line.sale_price,
                            'reference': raw_code,
                            'code': stock_line.product_id.default_code
                        }
                        stock_products.append(stocks_dict)

                    s_customers = request.env['customer.secondary'].sudo().search(
                        [('partner_id', '=', distributor.id)])
                    secondary_customers = []
                    for s_customer in s_customers:
                        reference_code = s_customer.outlet_code
                        if reference_code and '/' in reference_code:
                            x = reference_code.split('/')[1:]
                            reference_code = x[0]
                        sc_dict = {
                            'id': s_customer.id,
                            'name': s_customer.name,
                            'outlet_code': s_customer.outlet_code,
                            'address': s_customer.address,
                            'mobile': s_customer.mobile,
                            'reference_code': reference_code
                        }
                        secondary_customers.append(sc_dict)

                    rec_dict = {'customers': secondary_customers,
                                'stock_products': stock_products}
                    # records.append(rec_dict)

            msg = json.dumps(rec_dict,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ss_sc_01',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/order/distributors', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_secondary_sale_order_distributors(self, **kwargs):
        try:
            employee = request.env['hr.employee'].sudo().browse(request.em_id)
            customers = request.env['res.partner'].sudo().search(
                [('responsible', '=', employee.id), ('is_customer', '=', True)])
            records = []
            for customer in customers:
                stock = request.env['primary.customer.stocks'].sudo().browse([('customer_id', '=', customer.id)])
                if stock:
                    reference_code = customer.code
                    if reference_code and '/' in reference_code:
                        x = reference_code.split('/')[1:]
                        reference_code = x[0]
                    customer_dict = {'id': customer.id,
                                     'name': customer.name,
                                     'reference': reference_code,
                                     # 'stock_products': stock_products,
                                     'code': customer.code}
                    records.append(customer_dict)
            msg = json.dumps(records,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ss_sso_01',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/order/create', auth='none', type='http', csrf=False, methods=['POST'])
    def create_order(self, **kwargs):
        try:
            data = request.httprequest.data
            data_in_json = json.loads(data)
            # _logger.warning(f' ----- - {data_in_json}')
            distributor = request.env['res.partner'].sudo().search([('id', '=', data_in_json['distributor'])])
            distributor_stock = request.env['primary.customer.stocks'].sudo().search(
                [('customer_id', '=', distributor.id)])
            s_customer = request.env['customer.secondary'].sudo().search([('id', '=', data_in_json['customer'])])
            latitude = data_in_json['lat']
            longitude = data_in_json['lon']

            order_lines = []
            for product_data in data_in_json['products']:
                product = request.env['product.product'].sudo().search([('id', '=', product_data['id'])])
                order_line_dict = {
                    'product_id': product.id,
                    'quantity': product_data['quantity'],
                    'sale_price_unit': product_data['price'],
                    'stock_id': distributor_stock.id,
                }
                order_lines.append((0, 0, order_line_dict))

            order_vals = {
                'primary_customer_id': distributor.id,
                'secondary_customer_id': s_customer.id,
                'sale_line_ids': order_lines,
                'latitude': latitude,
                'longitude': longitude
            }

            order_id = request.env['sale.secondary'].sudo().create(order_vals)

            order_details = {
                'id': order_id.id,
                'name': order_id.name
            }
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='fun_ps_01',
            #                                      trace_ref='expected_primary_sale_order_create', with_location=False)
            msg = json.dumps(order_details,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ps_05',
            #                                      trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/order/confirm', auth='none', type='http', csrf=False, methods=['POST'])
    def secondary_sale_order_confirm(self, **kwargs):
        try:
            employee = request.env['hr.employee'].sudo().browse(request.em_id)
            order_id = request.env['sale.secondary'].sudo().search(
                [('id', '=', kwargs['order_id']), ('responsible_id', '=', employee.id)])
            if order_id and order_id.state == 'draft':
                order_id.action_confirm_secondary_sale()
                bol = True
                value = 'Secondary Sale order confirmed successfully'
            else:
                bol = False
                value = 'You are not allowed to confirm this sale order'
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='fun_ps_01',
            #                                      trace_ref='expected_primary_sale_order_create', with_location=False)
            msg = json.dumps({'result': bol, 'data': value},
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ps_05',
            #                                      trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/order/delete', auth='none', type='http', csrf=False, methods=['POST'])
    def secondary_sale_order_delete(self, **kwargs):
        try:
            employee = request.env['hr.employee'].sudo().browse(request.em_id)
            order_id = request.env['sale.secondary'].sudo().search(
                [('id', '=', kwargs['order_id']), ('responsible_id', '=', employee.id)])
            if order_id and order_id.state == 'draft':
                bol = order_id.unlink()
                value = 'Secondary sale order deleted successfully'
            else:
                bol = False
                value = 'You are not allowed to delete this sale order'
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='fun_ps_01',
            #                                      trace_ref='expected_primary_sale_order_create', with_location=False)
            msg = json.dumps({'result': bol, 'data': value},
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ps_05',
            #                                      trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/order/my', website=True, auth='none', type='http', csrf=False, methods=['GET'])
    def get_employee_all_secondary_sales(self, **kwargs):
        try:
            start_date = datetime.strptime(kwargs["start_date"], '%Y-%m-%d')
            end_date = datetime.strptime(kwargs["end_date"], '%Y-%m-%d')
            modified_end_date = end_date + timedelta(days=1)
            including_subordinates = []
            employee = request.env['hr.employee'].sudo().browse(request.em_id)
            including_subordinates.append(employee)
            including_subordinates.extend(self.get_subordinates(employee))

            my_orders = []
            secondary_sale_ids = request.env['sale.secondary'].sudo().search(
                [('responsible_id', 'in', [i_sub.id for i_sub in including_subordinates])])

            for order in secondary_sale_ids:
                if start_date <= order.create_date < modified_end_date:
                    millisec = order.create_date.timestamp() * 1000
                    localized_date_time = order.create_date.astimezone(pytz.timezone("Asia/Dhaka")).strftime(
                        "%Y-%m-%d %I:%M %p")
                    # _logger.warning(f' 1st============== {order.create_date}')
                    # _logger.warning(f' 2nd============== {localized_date_time}')

                    sale_dict = {'id': order.id, 'name': order.name, 'total': order.price_total,
                                 'sate': order.state, 'responsible_id': order.responsible_id.id,
                                 'distributor': order.primary_customer_id.name, 'date': localized_date_time,
                                 'date_long': int(millisec), 'customer': order.secondary_customer_id.name,
                                 'responsible': order.responsible_id.name}
                    my_orders.append(sale_dict)

            my_orders.sort(key=lambda x: x['id'], reverse=True)
            msg = json.dumps(my_orders,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ps_01',
            #                                      trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/order/info', auth='none', type='http', csrf=False, methods=['POST'])
    def get_secondary_sale_order_info(self, **kwargs):
        try:
            order_id = request.env['sale.secondary'].sudo().search([('id', '=', kwargs['order_id'])])
            if order_id:
                lines = []
                for sale_line in order_id.sale_line_ids:
                    order_line_dict = {
                        'id': sale_line.id,
                        'product_id': sale_line.product_id.id,
                        'product_name': sale_line.product_id.name,
                        'product_code': sale_line.product_id.default_code,
                        'quantity': sale_line.quantity,
                        'price_unit': sale_line.sale_price_unit,
                        'sub_total': sale_line.sub_total
                    }
                    lines.append(order_line_dict)
                localized_date_time = order_id.create_date.astimezone(pytz.timezone("Asia/Dhaka")).strftime(
                    "%Y-%m-%d %I:%M %p")
                order_dict = {
                    'distributor_id': order_id.primary_customer_id.id,
                    'distributor_name': order_id.primary_customer_id.name,
                    'distributor_code': order_id.primary_customer_id.code,
                    'distributor_mobile': order_id.distributor_mobile,
                    'distributor_address': order_id.distributor_address,
                    'responsible': order_id.responsible_id.name,
                    'customer': order_id.secondary_customer_id.name,
                    'customer_code': order_id.secondary_customer_id.outlet_code,
                    'customer_mobile': order_id.secondary_customer_mobile,
                    'customer_address': order_id.secondary_customer_address,
                    'status': order_id.state,
                    'order_date': localized_date_time,
                    'items': lines,
                }
            else:
                order_dict = {
                    'error': 'Secondary sale order not found'
                }
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='fun_ps_01',
            #                                      trace_ref='expected_primary_sale_order_create', with_location=False)
            msg = json.dumps(order_dict,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ps_05',
            #                                      trace_ref=str(e), with_location=False)
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
