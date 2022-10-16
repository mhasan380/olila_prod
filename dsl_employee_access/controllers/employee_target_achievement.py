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


class EmployeeTargetAchievement(http.Controller):

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/employee/team', website=True, auth='none', type='http', csrf=False, methods=['GET'])
    def get_team_target_achievement(self, **kwargs):
        try:
            _logger.warning(f' ============== ' + str(kwargs['empl']) + ' -- ' + str(kwargs['unauthorize']))
            employee = request.env['hr.employee'].sudo().search([('id', '=', kwargs['empl'])])
            employees = self.get_subordinates(employee)

            sub_tree = [
                {'id': employee.id, 'name': employee.name, 'mail': employee.work_email, 'phone': employee.work_phone,
                 'job_title': employee.job_title, 'manager_id': employee.parent_id.id,
                 'manager': employee.parent_id.name, 'photo': employee.image_1920, 'type': employee.type,
                 'target': employee.target, 'achievement': employee.archivement}]
            for record in employees:
                employee_dict = {}
                employee_dict['id'] = record.id
                employee_dict['name'] = record.name
                employee_dict['mail'] = record.work_email
                employee_dict['phone'] = record.work_phone
                employee_dict['job_title'] = record.job_title
                employee_dict['manager_id'] = record.parent_id.id
                employee_dict['manager'] = record.parent_id.name
                employee_dict['photo'] = record.image_1920
                employee_dict['type'] = record.type
                employee_dict['target'] = record.target
                employee_dict['achievement'] = record.archivement
                sub_tree.append(employee_dict)

            msg = json.dumps(sub_tree,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    def get_subordinates(self, employee):
        subordinate_list = []
        subordinates = request.env['hr.employee'].sudo().search([('parent_id', '=', employee.id)])
        subordinate_list.extend(subordinates)
        for subordinate in subordinates:
            subordinate_list.extend(self.get_subordinates(subordinate))

        return subordinate_list
