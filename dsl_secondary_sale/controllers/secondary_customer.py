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


class SecondaryCustomer(http.Controller):

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/create/customer', auth='none', type='http', csrf=False, methods=['POST'])
    def create_secondary_customer(self, **kwargs):
        try:

            msg = json.dumps({'yyy': 'gooo'},
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ss_sc_01',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/sellers', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_secondary_sellers(self, **kwargs):
        try:
            employee = request.env['hr.employee'].sudo().browse(request.em_id)
            customers = request.env['res.partner'].sudo().search(
                [('responsible', '=', employee.id), ('is_customer', '=', True)])
            records = []
            for customer in customers:
                reference_code = customer.code
                if reference_code and '/' in reference_code:
                    x = reference_code.split('/')[1:]
                    reference_code = x[0]
                customer_dict = {'id': customer.id,
                                 'name': customer.name,
                                 'warehouse_id': customer.deport_warehouse_id.id,
                                 'warehouse': customer.deport_warehouse_id.name,
                                 'contact_no': customer.mobile,
                                 'address': customer.street,
                                 'secondary_contact': customer.secondary_contact_persion,
                                 'zone': customer.zone_id.name,
                                 'reference': reference_code,
                                 'code': customer.code}
                records.append(customer_dict)
            msg = json.dumps(records,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ss_sc_02',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/customers', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_secondary_customers(self, **kwargs):
        try:
            employee = request.env['hr.employee'].sudo().browse(request.em_id)
            customers = request.env['customer.secondary'].sudo().search([('responsible_id', '=', employee.id)])

            records = []
            for customer in customers:
                reference_code = customer.outlet_code
                if customer.enabled and reference_code and '/' in reference_code:
                    x = reference_code.split('/')[1:]
                    reference_code = x[0]
                customer_dict = {'id': customer.id,
                                 'name': customer.name,
                                 'distributor_id': customer.partner_id.id,
                                 'distributor': customer.partner_id.name,
                                 'contact_no': customer.mobile,
                                 'address': customer.address,
                                 'responsible_id': customer.responsible_id.id,
                                 'responsible': customer.responsible_id.name,
                                 'reference': reference_code,
                                 'outlet_code': customer.outlet_code}
                records.append(customer_dict)
            msg = json.dumps(records,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ss_sc_03',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/customer/create', auth='none', type='http', csrf=False, methods=['POST'])
    def create_order(self, **kwargs):
        try:
            data = request.httprequest.data
            data_in_json = json.loads(data)
            # _logger.warning(f' ----- - {data_in_json}')
            distributor = request.env['res.partner'].sudo().search([('id', '=', data_in_json['distributor'])])

            vals = {
                'name': data_in_json['name'],
                'address': data_in_json['address'],
                'mobile': data_in_json['mobile'],
                'email': data_in_json['email'],
                'partner_id': distributor.id,
                'phone': data_in_json['phone']
            }

            if distributor:
                customer_id = request.env['customer.secondary'].sudo().create(vals)
                customer_details = {
                    'id': customer_id.id,
                    'name': customer_id.outlet_code
                }
            else:
                customer_details = {
                    'id': 0,
                    'name': ''
                }

            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='fun_ps_01',
                                                 trace_ref='expected_primary_sale_order_create',
                                                 with_location=False)
            msg = json.dumps(customer_details,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ss_sc_04',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)
