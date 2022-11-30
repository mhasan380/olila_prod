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


class SecondaryStock(http.Controller):

    @tools.security.protected_rafiul()
    @http.route('/web/sales_secondary/distributor/stocks', auth='none', type='http', csrf=False, methods=['POST'])
    def get_secondary_stocks(self, **kwargs):
        try:
            distributor = request.env['res.partner'].sudo().search([('id', '=', kwargs['distributor'])])
            stock = request.env['primary.customer.stocks'].sudo().search([('customer_id', '=', distributor.id)])
            stock_products = []

            if stock:
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
            msg = json.dumps(stock_products,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            # tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_ss_sc_02',
            #                                      trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)
