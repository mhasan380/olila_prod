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
        _logger.warning(f'========================= expired')
        emp.access_token = False
        return False
    else:
        _logger.warning(f'========================= not expired')
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
            headers = http.request.httprequest.headers
            if not headers['Authorization']:
                unauthorized_message = json.dumps({'state': 'failed', 'error': 'unauthorized access'},
                                                  sort_keys=True, indent=4, cls=ResponseEncoder)
                return http.Response(unauthorized_message, content_type='application/json;charset=utf-8', status=401)
            token_verified, empl = verify_token(header_token=headers['Authorization'], request=http.request)
            if token_verified and empl:
                kwargs.update({'empl': empl, 'unauthorize': False})
                http.request.em_id = empl
            else:
                kwargs.update({'empl': False, 'unauthorize': True})

                unauthorized_message = json.dumps({'state': 'failed', 'error': 'unauthorized access'},
                                                  sort_keys=True, indent=4, cls=ResponseEncoder)
                return http.Response(unauthorized_message, content_type='application/json;charset=utf-8', status=401)
            # _logger.warning(f'========================= {str(kwargs)}')
            # _logger.warning('================================ token ' + headers['Authorization'])
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
            headers = http.request.httprequest.headers
            token_verified = verify_public_token(header_token=headers['Authorization'], request=http.request)
            if token_verified:
                kwargs.update({'unauthorize': False})
            else:
                kwargs.update({'unauthorize': True})

                unauthorized_message = json.dumps({'state': 'failed', 'error': 'unauthorized client'},
                                                  sort_keys=True, indent=4, cls=ResponseEncoder)
                return http.Response(unauthorized_message, content_type='application/json;charset=utf-8', status=401)
            # _logger.warning(f'========================= {str(kwargs)}')
            # _logger.warning('================================ token ' + headers['Authorization'])
            return func(*args, **kwargs)

        return verify_client

    return wrapper
