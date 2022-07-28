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


class SaleReturnPrimary(http.Controller):

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/returnable/orders', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_returnable_sale_orders(self, **kwargs):
        try:
            start_date = datetime.strptime(kwargs["start_date"], '%Y-%m-%d')
            end_date = datetime.strptime(kwargs["end_date"], '%Y-%m-%d')

            my_sale_orders = request.env['sale.order'].sudo().search(
                [('responsible.id', '=', request.em_id), ('state', '=', 'sale')])
            _logger.warning(f' ============== ' + str(len(my_sale_orders)))
            my_orders = []
            for order in my_sale_orders:
                if start_date <= order.date_order < end_date and order.delivery_count > 0:
                    millisec = order.date_order.timestamp() * 1000
                    sale_dict = {'id': order.id, 'name': order.name, 'total': order.amount_total, 'sate': order.state,
                                 'customer': order.partner_id.name, 'date': order.date_order, 'date_long': millisec}
                    my_orders.append(sale_dict)

            msg = json.dumps(my_orders,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/returnable/order/detail', auth='none', type='http', csrf=False, methods=['POST'])
    def get_returnable_order_detail(self, **kwargs):
        try:

            returnable_order = request.env['sale.order'].sudo().browse(int(kwargs["order_id"]))

            pickings = []
            for picking in returnable_order.picking_ids:
                if picking.picking_type_id.code == 'outgoing':
                    picking_dict = {}
                    picking_dict['id'] = picking.id
                    picking_dict['name'] = picking.name
                    picking_dict['customer_id'] = picking.partner_id.id
                    picking_dict['customer'] = picking.partner_id.name
                    picking_dict['from_location_id'] = picking.location_id.id
                    picking_dict['from_location_name'] = picking.location_id.name
                    picking_dict['dest_location_id'] = picking.location_dest_id.id
                    picking_dict['dest_location_name'] = picking.location_dest_id.name
                    picking_dict['sale_type'] = picking.sale_type
                    picking_dict['document'] = picking.origin
                    # move_lines = []
                    # for line in picking.move_line_ids_without_package:
                    #     move_line_dict = {}
                    #     move_line_dict['product_id'] = line.product_id.id
                    #     move_line_dict['product_name'] = line.product_id.name
                    #     move_line_dict['quantity'] = line.qty_done
                    #     move_lines.append(move_line_dict)
                    # picking_dict['move_lines'] = move_lines

                    returnPicking = request.env['stock.return.picking'].sudo().browse(picking.id)
                    move_lines = []
                    # for move_line in returnPicking.product_return_moves:
                    for stock_move in picking.move_lines:
                        quantity = stock_move.product_qty
                        for move in stock_move.move_dest_ids:
                            if move.origin_returned_move_id and move.origin_returned_move_id != stock_move:
                                continue
                            if move.state in ('partially_available', 'assigned'):
                                quantity -= sum(move.move_line_ids.mapped('product_qty'))
                            elif move.state in ('done'):
                                quantity -= move.product_qty
                        quantity = float_round(quantity, precision_rounding=stock_move.product_id.uom_id.rounding)
                        move_line_dict = {}
                        move_line_dict['product_id'] = stock_move.product_id.id
                        move_line_dict['move_id'] = stock_move.id
                        move_line_dict['product_name'] = stock_move.product_id.name
                        move_line_dict['quantity'] = quantity
                        move_lines.append(move_line_dict)
                    picking_dict['move_lines'] = move_lines

                    pickings.append(picking_dict)

            return_details = {
                'name': returnable_order.name,
                'id': returnable_order.id,
                'customer_id': returnable_order.partner_id.id,
                'customer': returnable_order.partner_id.name,
                'customer_code': returnable_order.partner_id.code,
                'delivery_pickings': pickings
            }

            msg = json.dumps(return_details,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/returnable/order/return', auth='none', type='http', csrf=False, methods=['POST'])
    def create_return(self, **kwargs):
        try:
            data = request.httprequest.data
            data_in_json = json.loads(data)
            picking = data_in_json['picking_id']
            products = data_in_json['products']
            picking_id = request.env['stock.picking'].sudo().browse(int(picking))

            picking_type_id = picking_id.picking_type_id.return_picking_type_id.id or picking_id.picking_type_id.id
            state = 'draft'
            origin = _("Return of %s", picking_id.name)
            location_id = picking_id.location_dest_id.id
            location_dest_id = picking_id.location_id.id

            # stock_return_picking = request.env['stock.return.picking'].sudo().

            stock_return_picking = request.env['stock.return.picking'].sudo().create(
                {
                    'picking_id': picking_id.id,
                    # 'product_return_moves': picking_id.id,
                    'location_id': location_dest_id
                }
            )

            stock_return_picking._onchange_picking_id()
            for line in stock_return_picking.product_return_moves:
                for product in products:
                    print(product['product_id'])
                    print(product['quantity'])
                    if line.product_id.id == product['product_id']:
                        line.quantity = product['quantity']
                    else:
                        line.unlink()
                if len(products) == 0:
                    line.unlink()

            new_picking_id, pick_type_id = stock_return_picking._create_returns()

            # auto fill done
            # pickings_to_do = request.env['stock.picking'].sudo().search([('id','=',new_picking_id)])
            # pickings_not_to_do = request.env['stock.picking']
            # for picking_data in pickings_to_do:
            #     for move in picking_data.move_lines.filtered(lambda m: m.state not in ['done', 'cancel']):
            #         for move_line in move.move_line_ids:
            #             move_line.qty_done = move_line.product_uom_qty
            # pickings_to_validate = request.env.context.get('button_validate_picking_ids')
            # if pickings_to_validate:
            #     pickings_to_validate = request.env['stock.picking'].browse(pickings_to_validate)
            #     pickings_to_validate = pickings_to_validate - pickings_not_to_do
            #     pickings_to_validate.with_context(skip_immediate=True).button_validate()

            newly_created = request.env['stock.picking'].sudo().browse(new_picking_id)

            picking_details = {
                'id': newly_created.id,
                'name': newly_created.name
            }

            msg = json.dumps(picking_details,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)
