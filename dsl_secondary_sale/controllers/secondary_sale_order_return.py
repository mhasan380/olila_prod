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
    @http.route('/web/sales_secondary/order/return', auth='none', type='http', csrf=False, methods=['POST'])
    def create_order(self, **kwargs):
        try:
            data = request.httprequest.data
            data_in_json = json.loads(data)
            order_id = data_in_json['order_id']
            products = data_in_json['products']

            ss_order = request.env['sale.secondary'].sudo().search([('id', '=', order_id)])

            result = 'Secondary sale return done successfully.'
            bol = True
            if ss_order:
                for product in products:
                    product_id = request.env['product.product'].sudo().search([('id', '=', product['product_id'])])
                    if product_id:
                        stock_id = request.env['primary.customer.stocks'].sudo().search(
                            [('customer_id', '=', ss_order.primary_customer_id.id)])
                        return_vals = {
                            'secondary_sale_id': ss_order.id,
                            'secondary_stock_id': stock_id.id,
                            'product_id': product_id.id,
                            'quantity': product['quantity'],
                            'remarks': product['remarks'],
                            'type': 'in',
                            'secondary_customer_id': ss_order.secondary_customer_id.id
                        }
                        request.env['stock.move.secondary'].sudo().create(return_vals)
                    else:
                        result = 'Product not found. Unable to return.'
                        bol = False
            else:
                result = 'Unable to create secondary sale return.'
                bol = False

            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='fun_ps_01',
            #                                      trace_ref='expected_primary_sale_order_create', with_location=False)
            msg = json.dumps({'result': bol, 'data': result},
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ps_05',
            #                                      trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/order/returnable', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_secondary_sale_order_returnable(self, **kwargs):
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
                [('responsible_id', 'in', [i_sub.id for i_sub in including_subordinates]), ('state', '=', 'confirmed')])

            for order in secondary_sale_ids:
                if start_date <= order.create_date < modified_end_date:
                    millisec = order.create_date.timestamp() * 1000
                    localized_date_time = order.create_date.astimezone(pytz.timezone("Asia/Dhaka")).strftime(
                        "%Y-%m-%d %I:%M %p")
                    # _logger.warning(f' 1st============== {order.create_date}')
                    # _logger.warning(f' 2nd============== {localized_date_time}')

                    sale_dict = {'id': order.id, 'name': order.name, 'total': order.net_amount,
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

    # @tools.security.protected_rafiul()
    # @http.route('/web/sales_secondary/order/info', auth='none', type='http', csrf=False, methods=['POST'])
    # def get_secondary_sale_order_info(self, **kwargs):
    #     try:
    #         order_id = request.env['sale.secondary'].sudo().search([('id', '=', kwargs['order_id'])])
    #         if order_id:
    #             lines = []
    #             for sale_line in order_id.sale_line_ids:
    #                 order_line_dict = {
    #                     'id': sale_line.id,
    #                     'product_id': sale_line.product_id.id,
    #                     'product_name': sale_line.product_id.name,
    #                     'product_code': sale_line.product_id.default_code,
    #                     'quantity': sale_line.quantity,
    #                     'price_unit': sale_line.sale_price_unit,
    #                     'sub_total': sale_line.sub_total
    #                 }
    #                 lines.append(order_line_dict)
    #             localized_date_time = order_id.create_date.astimezone(pytz.timezone("Asia/Dhaka")).strftime(
    #                 "%Y-%m-%d %I:%M %p")
    #             order_dict = {
    #                 'distributor_id': order_id.primary_customer_id.id,
    #                 'distributor_name': order_id.primary_customer_id.name,
    #                 'distributor_code': order_id.primary_customer_id.code,
    #                 'distributor_mobile': order_id.distributor_mobile,
    #                 'distributor_address': order_id.distributor_address,
    #                 'responsible': order_id.responsible_id.name,
    #                 'customer': order_id.secondary_customer_id.name,
    #                 'customer_code': order_id.secondary_customer_id.outlet_code,
    #                 'customer_mobile': order_id.secondary_customer_mobile,
    #                 'customer_address': order_id.secondary_customer_address,
    #                 'status': order_id.state,
    #                 'order_date': localized_date_time,
    #                 'items': lines,
    #             }
    #         else:
    #             order_dict = {
    #                 'error': 'Secondary sale order not found'
    #             }
    #         # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='fun_ps_01',
    #         #                                      trace_ref='expected_primary_sale_order_create', with_location=False)
    #         msg = json.dumps(order_dict,
    #                          sort_keys=True, indent=4, cls=ResponseEncoder)
    #         return Response(msg, content_type='application/json;charset=utf-8', status=200)
    #
    #     except Exception as e:
    #         err = {'error': str(e)}
    #         # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ps_05',
    #         #                                      trace_ref=str(e), with_location=False)
    #         error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
    #         return Response(error, content_type='application/json;charset=utf-8', status=200)

    def get_subordinates(self, employee):
        subordinate_list = []
        subordinates = request.env['hr.employee'].sudo().search(
            [('parent_id', '=', employee.id), '|', ('active', '=', True), ('active', '=', False)])
        subordinate_list.extend(subordinates)
        for subordinate in subordinates:
            subordinate_list.extend(self.get_subordinates(subordinate))

        return subordinate_list
