###################################################################################
#
#    Copyright (c) Daffodil Computers Ltd.
#
#    This file is part of Empolyee based REST API for Odoo
#    (see https://daffodil.computers).
#
#    DCL Proprietary License v1.0
#
#    This software and associated files (the "Software") may only be used 
#    (executed, modified, executed after modifications) if you have
#    purchased a valid license from DCL.
#
#    The above permissions are granted for a single database per purchased 
#    license. Furthermore, with a valid license it is permitted to use the
#    software on other databases as long as the usage is limited to a testing
#    or development environment.
#
#    You may develop modules based on the Software or that use the Software
#    as a library (typically by depending on it, importing it and using its
#    resources), but without copying any source code or material from the
#    Software. You may distribute those modules under the license of your
#    choice, provided that this license is compatible with the terms of the 
#    DCL Proprietary License (For example: LGPL, MIT, or proprietary licenses
#    similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###################################################################################

import re
import logging
import functools
import base64

from urllib.parse import urlencode, quote_plus
from urllib.parse import urlparse, urlunparse, parse_qs
from werkzeug.exceptions import Unauthorized, Forbidden

import json, ast
from odoo import http, api, SUPERUSER_ID
from datetime import date, datetime, time
from odoo.addons.dsl_employee_access.tools.json import ResponseEncoder
import geocoder

_logger = logging.getLogger(__name__)


def decoded_b64(b64str):
    base64_bytes = b64str.encode('ascii')
    d_bytes = base64.b64decode(base64_bytes)
    return d_bytes.decode('ascii')


def extract_token_validity(d_part):
    d_dict = decoded_b64(d_part)
    res = ast.literal_eval(d_dict)
    return decoded_b64(res['tt'])


def check_token_validity(emp):
    token = emp.access_token
    time_n = datetime.strptime(emp.get_date_time_now(), "%Y-%m-%d %H:%M:%S")
    time_ex = datetime.strptime(extract_token_validity(token[11:]), "%Y-%m-%d %H:%M:%S")
    # ----------------------------expire token after 24 hour
    exp_time = datetime.strptime("1996-05-16 23:59:59", "%Y-%m-%d %H:%M:%S") - datetime.strptime(
        "1996-05-16 00:00:01", "%Y-%m-%d %H:%M:%S")
    # exp_time = datetime.strptime("1996-05-16 23:59:55", "%Y-%m-%d %H:%M:%S") - datetime.strptime(
    #     "1996-05-16 23:59:45", "%Y-%m-%d %H:%M:%S")

    if time_n - time_ex > exp_time:
        # _logger.warning(f'========================= expired')
        emp.access_token = False
        return False
    else:
        # _logger.warning(f'========================= not expired')
        return True


def verify_token(header_token=False, request=False):
    try:
        if header_token and request:
            emp = request.env['hr.employee'].sudo().search(
                [('access_token', '=', header_token)])
            if emp and check_token_validity(emp):
                return True, emp.id
        return False, False
    except Exception:
        return False, False


def protected_rafiul(operations=['read'], check_custom_routes=False, *args, **kwargs):
    def wrapper(func):
        @functools.wraps(func)
        def verify(*args, **kwargs):
            # create_log_salesforce(http.request, access_type='protected', system_returns='functionality',
            #                       trace_ref='olila-OP-002')
            headers = http.request.httprequest.headers
            if not headers['Authorization']:
                unauthorized_message = json.dumps({'state': 'failed', 'error': 'unauthorized access'},
                                                  sort_keys=True, indent=4, cls=ResponseEncoder)
                return http.Response(unauthorized_message, content_type='application/json;charset=utf-8', status=401)
            token_verified, empl = verify_token(header_token=headers['Authorization'], request=http.request)
            if token_verified and empl:
                kwargs.update({'empl': empl, 'unauthorize': False})
                http.request.em_id = empl
                # create_log_salesforce(http.request, access_type='protected', system_returns='functionality',
                #                       trace_ref='olila-OP-003')
            else:
                kwargs.update({'empl': False, 'unauthorize': True})
                _logger.warning('------------------- test111')
                # create_log_salesforce(http.request, access_type='protected',
                #                       system_returns='functionality_unauthorized',
                #                       trace_ref='olila-OP-002')
                unauthorized_message = json.dumps({'state': 'failed', 'error': 'unauthorized access'},
                                                  sort_keys=True, indent=4, cls=ResponseEncoder)
                return http.Response(unauthorized_message, content_type='application/json;charset=utf-8', status=401)
            return func(*args, **kwargs)
        return verify
    return wrapper


def verify_public_token(header_token=False, request=False):
    try:

        if header_token and request:
            config_record = request.env['app.config'].sudo().search([], limit=1)
            if config_record:
                if header_token != config_record.public_token:
                    return False
                return True
            else:
                vals = {
                    'public_token': 'ZWpqoqxy8P#wdRSJRAFIULXXXDlnuXm3HlXCZoDBztt',
                    'version_down': '0.0',
                    'version_up': '0.0',
                    'version_code': 0,
                    'custom_message': '',
                    'is_under_maintenance': False
                }
                created = request.env['app.config'].sudo().create(vals)
                if created:
                    return True
                else:
                    return False
        return False
    except Exception as e:
        return False


def public_rafiul(operations=['read'], check_custom_routes=False, *args, **kwargs):
    def wrapper(func):
        @functools.wraps(func)
        def verify_client(*args, **kwargs):
            trace_mail = ''
            if 'mail' in kwargs:
                trace_mail = kwargs['mail']
            headers = http.request.httprequest.headers
            token_verified = verify_public_token(header_token=headers['Authorization'], request=http.request)
            if token_verified:
                kwargs.update({'unauthorize': False})
                # create_log_salesforce(http.request, access_type='public', system_returns='authorized_client',
                #                       trace_ref=trace_mail)
            else:
                kwargs.update({'unauthorize': True})
                # create_log_salesforce(http.request, access_type='public', system_returns='unauthorized_client',
                #                       trace_ref=trace_mail)
                unauthorized_message = json.dumps({'state': 'failed', 'error': 'unauthorized client'},
                                                  sort_keys=True, indent=4, cls=ResponseEncoder)
                return http.Response(unauthorized_message, content_type='application/json;charset=utf-8', status=401)
            return func(*args, **kwargs)
        return verify_client
    return wrapper


def create_log_salesforce(request, access_type, system_returns, trace_ref):
    try:
        headers = request.httprequest.headers

        trace_ip_address = ""
        trace_mac = ""

        employee_id = False
        if hasattr(request, 'em_id') and request.em_id:
            employee_id = request.env['employee.logger.salesforce'].sudo().browse(request.em_id).id

        if not trace_mac:
            trace_mac = request.httprequest.environ.get('HTTP_USER_AGENT', '')
        if not trace_ip_address:
            trace_ip_address = request.httprequest.environ.get('REMOTE_ADDR', '')

        if trace_ip_address:
            g = geocoder.ip(trace_ip_address)
        else:
            g = geocoder.ip('me')
        g_location = f'{str(g.city)}, {str(g.state)}, {str(g.country)}'

        vals = {
            'access_type': access_type,
            'name': request.httprequest.url,
            'access_credential': headers['Authorization'],
            'employee_id': employee_id,
            'trace_ip_address': trace_ip_address,
            'trace_agent': trace_mac,
            'trace_latlng': g.latlng,
            'system_returns': system_returns,
            'trace_location': g_location,
            'trace_ref': trace_ref
        }
        created = request.env['employee.logger.salesforce'].sudo().create(vals)
        # _logger.warning(f'--------------------{str(created)}')
    except Exception as e:
        # _logger.warning(f'--------------------{str(e)}')
        pass
