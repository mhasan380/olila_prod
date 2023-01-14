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
from odoo.tools.float_utils import float_round
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


class RoutePlanV2APIs(http.Controller):

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/routes/master/type', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_master_routes_by_type(self, **kwargs):
        try:
            route_master = request.env['route.master'].sudo().search([], order='id desc')
            primary = []
            secondary = []
            for master in route_master:
                if master.route_type == 'primary':
                    primary_customers = []
                    for primary_customer_id in master.primary_customer_ids:
                        pc_dict = {
                            'id': primary_customer_id.customer_id.id,
                            'name': primary_customer_id.customer_id.name,
                            'code': primary_customer_id.customer_code,
                        }
                        primary_customers.append(pc_dict)
                    primary_dict = {}
                    primary_dict['id'] = master.id
                    primary_dict['name'] = master.name
                    primary_dict['route_id'] = master.route_id
                    primary_dict['so_market'] = master.area_id.name
                    primary_dict['territory'] = master.territory_id.name
                    primary_dict['region'] = master.zone_id.name
                    primary_dict['type'] = master.route_type
                    primary_dict['coverage'] = master.coverage
                    primary_dict['customers'] = primary_customers
                    primary.append(primary_dict)

                if master.route_type == 'secondary':
                    secondary_customers = []
                    for secondary_customer_id in master.secondary_customer_ids:
                        sc_dict = {
                            'id': secondary_customer_id.customer_id.id,
                            'name': secondary_customer_id.customer_id.name,
                            'code': secondary_customer_id.customer_code,
                        }
                        secondary_customers.append(sc_dict)
                    secondary_dict = {}
                    secondary_dict['id'] = master.id
                    secondary_dict['name'] = master.name
                    secondary_dict['route_id'] = master.route_id
                    secondary_dict['so_market'] = master.area_id.name
                    secondary_dict['territory'] = master.territory_id.name
                    secondary_dict['region'] = master.zone_id.name
                    secondary_dict['type'] = master.route_type
                    secondary_dict['coverage'] = master.coverage
                    secondary_dict['customers'] = secondary_customers
                    secondary.append(secondary_dict)

            records = {
                'primary': primary,
                'secondary': secondary
            }
            msg = json.dumps(records,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}

            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)
