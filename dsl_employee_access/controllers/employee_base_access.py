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


class EmployeeAccessBase(http.Controller):

    # @http.route('/employee_access/status', website=True, auth='none', type='http', csrf=False, methods=['GET'])
    # def employee_state(self, **kwargs):
    #
    #     try:
    #         employee_ = request.env['hr.employee'].sudo().browse(2)
    #
    #         status_dict = {"status": employee_.name}
    #
    #         response_ = json.dumps(status_dict, sort_keys=True, indent=4)
    #         return Response(response_, content_type='application/json;charset=utf-8', status=200)
    #
    #     except Exception as e:
    #         error = json.dumps({'status': str(e)}, sort_keys=True, indent=4)
    #         return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.public_rafiul()
    @http.route('/web/sales/force/sign/in', auth='none', type='http', csrf=False, methods=['POST'])
    def app_sign_in(self, **kwargs):
        try:

            # headers = request.httprequest.headers
            # if headers['Authorization'] == 'ZWpqoqxy8P#wdRSJRAFIULXXXDlnuXm3HlXCZoDBztt':
            if not kwargs['mail'] or not kwargs['code']:
                unauthorized_message = json.dumps({'state': 'failed', 'error': 'invalid parameter'}, sort_keys=True,
                                                  indent=4)
                return Response(unauthorized_message, content_type='application/json;charset=utf-8', status=200)

            this_employee_res = request.env['hr.employee'].sudo().search([('work_email', '=', kwargs['mail'])])
            # if self.is_employee_restricted(this_employee_res.id):

            if this_employee_res:
                # check if the employee is active and sales force is enabled
                if this_employee_res.is_enable_sales_force == False or this_employee_res.active_status == False:
                    message = json.dumps({'state': 'failed', 'status': 'Your access is currently not active'},
                                         sort_keys=True,
                                         indent=4, cls=ResponseEncoder)
                    return Response(message, content_type='application/json;charset=utf-8', status=200)

                if this_employee_res.is_wrong_code_limit_exceeded and self.make_wrong_code_limit_invalid(
                        this_employee_res.id):
                    # if self.make_wrong_code_limit_invalid(this_employee_res.id):
                    msg = json.dumps({'state': 'failed', 'status': 'You are restricted for one hour.'},
                                     sort_keys=True, indent=4, cls=ResponseEncoder)
                    return Response(msg, content_type='application/json;charset=utf-8', status=200)

            else:
                message = json.dumps({'state': 'failed', 'status': 'wrong email or access code'}, sort_keys=True,
                                     indent=4, cls=ResponseEncoder)
                return Response(message, content_type='application/json;charset=utf-8', status=200)

            employee = request.env['hr.employee'].sudo().search([('work_email', '=', kwargs['mail']),
                                                                 ('access_code_crypto', '=',
                                                                  this_employee_res.to_hash(kwargs['code']))])
            if employee:

                employee.access_token = self._token_generate(id=employee.id, mail=employee.work_email,
                                                             name=employee.name)
                message = json.dumps(
                    {'state': 'success', 'name': employee.name, 'mail': employee.work_email,
                     'access_token': employee.access_token},
                    sort_keys=True, indent=4, cls=ResponseEncoder)
                return Response(message, content_type='application/json;charset=utf-8', status=200)
            else:
                employee = request.env['hr.employee'].sudo().search([('work_email', '=', kwargs['mail'])])
                if employee:
                    self._check_and_restrict_for_one_hour(employee.id)
                message = json.dumps({'state': 'failed', 'status': 'wrong email or access code'}, sort_keys=True,
                                     indent=4, cls=ResponseEncoder)
                return Response(message, content_type='application/json;charset=utf-8', status=200)
            # else:
            #     unauthorized_message = json.dumps({'state': 'failed', 'error': 'unauthorized client'}, sort_keys=True,
            #                                       indent=4, cls=ResponseEncoder)
            #     return Response(unauthorized_message, content_type='application/json;charset=utf-8', status=401)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    def _check_and_restrict_for_one_hour(self, employee_id):
        now = request.env['hr.employee'].get_date_time_now()
        emp_ = request.env['hr.employee'].sudo().browse(employee_id)

        if emp_.wrong_code_time:
            emp_.wrong_code_count += 1

            that_time = datetime.strptime(emp_.wrong_code_time, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
            fixed_interval = datetime.strptime("1996-05-16 17:00:00", "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                "1996-05-16 16:00:00", "%Y-%m-%d %H:%M:%S")
            interval = current_time - that_time

            if fixed_interval > interval:
                if emp_.wrong_code_count > 3:
                    emp_.is_wrong_code_limit_exceeded = True
                else:
                    emp_.is_wrong_code_limit_exceeded = False
            else:
                emp_.is_wrong_code_limit_exceeded = False
                emp_.wrong_code_time = f'{now}'
                # if emp_.wrong_code_count == 5:
                #     emp_.wrong_code_count = 1
                # else:
                emp_.wrong_code_count = 0
        else:

            emp_.wrong_code_time = f'{now}'
            emp_.is_wrong_code_limit_exceeded = False
            emp_.wrong_code_count = 0

    def make_wrong_code_limit_invalid(self, employee_id):
        now = request.env['hr.employee'].get_date_time_now()
        emp_ = request.env['hr.employee'].sudo().browse(employee_id)
        if emp_.wrong_code_time:
            that_time = datetime.strptime(emp_.wrong_code_time, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
            fixed_interval = datetime.strptime("1996-05-16 17:00:00", "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                "1996-05-16 16:00:00", "%Y-%m-%d %H:%M:%S")
            interval = current_time - that_time

            if fixed_interval > interval:
                emp_.is_wrong_code_limit_exceeded = True
            else:
                emp_.is_wrong_code_limit_exceeded = False
        else:
            emp_.is_wrong_code_limit_exceeded = False

        return emp_.is_wrong_code_limit_exceeded

    def _token_generate(self, id, mail, name):
        token = ''.join(
            [choice(string.ascii_uppercase + string.ascii_lowercase + string.digits + '#@') for _ in
             range(11)])
        base64_time = self._toBase64Encode(request.env['hr.employee'].get_date_time_now())

        random_number = random.randint(1, 4)
        dta = {'mail': mail, 'name': name, token[4:9]: token[0:3], 'tt': base64_time}
        if random_number == 1:
            dta = {'name': name, 'tt': base64_time, 'mail': mail, token[0:3]: token[4:9]}
        elif random_number == 2:
            dta = {'tt': base64_time, token[0:3]: token[4:9], 'name': name, 'mail': mail}
        elif random_number == 3:
            dta = {token[0:3]: token[4:9], 'mail': mail, 'tt': base64_time, 'name': name}
        elif random_number == 4:
            dta = {token[0:3]: token[4:9], 'tt': base64_time, 'name': name, 'mail': mail}

        base64_data = self._toBase64Encode(dta)

        token += base64_data
        # token += base64_time

        return token

    def _toBase64Encode(self, data):
        data_bytes = str(data).encode('ascii')
        base64_bytes = base64.b64encode(data_bytes)
        return base64_bytes.decode('ascii')

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/employee/data', website=True, auth='none', type='http', csrf=False, methods=['GET'])
    def get_employee(self, **kwargs):
        try:
            _logger.warning(f' ============== ' + str(kwargs['empl']) + ' -- ' + str(kwargs['unauthorize']))
            employee = request.env['hr.employee'].sudo().search([('id', '=', kwargs['empl'])])
            employee_dict = {}
            employee_dict['id'] = employee.id
            employee_dict['name'] = employee.name
            employee_dict['mail'] = employee.work_email
            employee_dict['phone'] = employee.work_phone
            employee_dict['department_id'] = employee.department_id.id
            employee_dict['department'] = employee.department_id.name
            employee_dict['manager_id'] = employee.parent_id.id
            employee_dict['manager'] = employee.parent_id.name
            employee_dict['photo'] = employee.image_1920
            employee_dict['type'] = employee.type
            employee_dict['target'] = employee.target
            employee_dict['achievement'] = employee.archivement

            msg = json.dumps(employee_dict,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/employee/signout', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def employee_sign_out(self, **kwargs):
        try:
            employee = request.env['hr.employee'].sudo().browse(request.em_id)
            if employee:
                employee.access_token = self._token_generate(id=employee.id, mail=employee.work_email,
                                                             name=employee.name)
                info = {'result': True, 'data': "Successfully Logged Out."}
            else:
                info = {'result': False, 'data': "Can't Log out"}

            msg = json.dumps(info,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/employee/access_update', auth='none', type='http', csrf=False, methods=['POST'])
    def employee_code_update(self, **kwargs):
        try:

            if kwargs['new_code'] and kwargs['code']:
                employee = request.env['hr.employee'].sudo().browse(request.em_id)
                if employee.access_code_crypto == employee.to_hash(kwargs['code']):
                    employee.access_code_crypto = employee.to_hash(kwargs['new_code'])
                    if employee.to_hash(kwargs['new_code']) == employee.access_code_crypto:
                        info = {'result': True, 'data': 'You have successfully changed your access code.'}
                    else:
                        info = {'result': False,
                                'data': 'Failed to update your access code. Please contact with the administrator.'}
                else:
                    info = {'result': False, 'data': 'Wrong access code.'}
            else:
                info = {'result': False, 'data': 'Some fields are missing.'}

            msg = json.dumps(info,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)
