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


class AppConfigController(http.Controller):

    @tools.security.public_rafiul()
    @http.route('/web/sales/force/app/config', website=True, auth='none', type='http', csrf=False, methods=['GET'])
    def get_app_config(self, **kwargs):

        try:
            app_config = request.env['app.config'].sudo().search([])
            response_dict = {}
            if len(app_config) > 0:
                response_dict = {"status": 'success',
                                 "version_down": app_config[0].version_down,
                                 "version_up": app_config[0].version_up,
                                 "version_code": app_config[0].version_code,
                                 "custom_message": app_config[0].custom_message,
                                 "maintenance": app_config[0].is_under_maintenance,
                                 }

            response_ = json.dumps(response_dict, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(response_, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            error = json.dumps({'status': str(e)}, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.public_rafiul()
    @http.route('/web/sales/force/appConfigSet', auth='none', type='http', csrf=False, methods=['POST'])
    def set_app_config(self, **kwargs):
        try:
            vals= {}
            vals['custom_message'] = kwargs['custom_message']
            vals['version_down'] = kwargs['version_down']
            vals['version_up'] = kwargs['version_up']
            vals['version_code'] = kwargs['version_code']
            vals['custom_message'] = kwargs['custom_message']
            vals['is_under_maintenance'] = kwargs['maintenance']

            bol = request.env['app.config'].sudo().browse(1).write(vals)
            response_dict = {'updated': bol, 'status': 'success'}

            response_ = json.dumps(response_dict, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(response_, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            error = json.dumps({'status': str(e)}, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)
