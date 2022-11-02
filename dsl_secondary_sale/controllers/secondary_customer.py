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
    def get_secondary_customers(self, **kwargs):
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