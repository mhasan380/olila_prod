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
    @http.route('/web/sales/force/route/plans', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_route_plans(self, **kwargs):
        try:
            route_plans = request.env['sales.person.plan'].sudo().search(['|', ('assigned_to', '=', request.em_id),
                                                                          ('assigned_by', '=', request.em_id)],
                                                                         limit=50, order='id desc')
            records = []
            for route_plan in route_plans:
                plan_dict = {}
                plan_dict['id'] = route_plan.id
                plan_dict['name'] = route_plan.name
                plan_dict['start_date'] = route_plan.sales_plan_date
                plan_dict['end_date'] = route_plan.end_plan_date
                plan_dict['progress'] = route_plan.progress_rate
                plan_dict['assigned_by'] = route_plan.assigned_by.name
                plan_dict['assigned_to'] = route_plan.assigned_to.name
                tasks = []
                for task in route_plan.info_checklist:
                    task_dict = {}
                    task_dict['id'] = task.id
                    task_dict['name'] = task.name_work
                    task_dict['customer_id'] = task.customer.id
                    task_dict['customer'] = task.customer.name
                    task_dict['status'] = task.status
                    tasks.append(task_dict)
                # plan_dict['tasks'] = tasks
                records.append(plan_dict)

            msg = json.dumps(records,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/route/plan/create', auth='none', type='http', csrf=False, methods=['POST'])
    def route_plan_create(self, **kwargs):
        try:

            data = request.httprequest.data
            data_in_json = json.loads(data)
            plan_name = data_in_json['name']
            assigned_to = request.env['hr.employee'].sudo().search([('id', '=', data_in_json['assigned_to'])])
            assigned_by = request.env['hr.employee'].sudo().search([('id', '=', request.em_id)])
            start_date = date.today()
            end_date = data_in_json['end_date']
            tasks = data_in_json['tasks']

            task_lines = []
            for line in tasks:
                customer = request.env['res.partner'].sudo().search([('id', '=', line['customer_id'])])
                task_line_dict = {
                    'name_work': line['task_name'],
                    'customer': customer.id,
                    # 'check_in_latitude': line['check_in_latitude'],
                    # 'check_in_longitude': product_data['quantity'],
                    # 'check_out_latitude': product.lst_price,
                    # 'check_out_longitude': customer.discount
                }
                task_lines.append((0, 0, task_line_dict))

            vals = {
                'name': plan_name,
                'assigned_to': assigned_to.id,
                'assigned_by': assigned_by.id,
                'sales_plan_date': start_date,
                'end_plan_date': end_date,
                'info_checklist': task_lines,
            }

            route_plan_id = request.env['sales.person.plan'].sudo().create(vals)

            order_details = {
                'id': route_plan_id.id,
                'name': route_plan_id.name
            }

            msg = json.dumps(order_details,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/route/plan/info', auth='none', type='http', csrf=False, methods=['POST'])
    def route_plan_info(self, **kwargs):
        try:

            route_plan = request.env['sales.person.plan'].sudo().browse(int(kwargs['plan_id']))

            plan_dict = {}
            plan_dict['id'] = route_plan.id
            plan_dict['name'] = route_plan.name
            plan_dict['start_date'] = route_plan.sales_plan_date
            plan_dict['end_date'] = route_plan.end_plan_date
            plan_dict['progress'] = route_plan.progress_rate
            plan_dict['assigned_by'] = route_plan.assigned_by.name
            plan_dict['assigned_to'] = route_plan.assigned_to.name
            tasks = []
            for task in route_plan.info_checklist:
                task_dict = {}
                task_dict['id'] = task.id
                task_dict['name'] = task.name_work
                task_dict['customer_id'] = task.customer.id
                task_dict['customer'] = task.customer.name
                task_dict['status'] = task.status
                tasks.append(task_dict)
            plan_dict['tasks'] = tasks

            msg = json.dumps(plan_dict,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/route/plan/task_update', auth='none', type='http', csrf=False, methods=['POST'])
    def route_plan_task_update(self, **kwargs):
        try:

            task = request.env['rode.list'].sudo().browse(int(kwargs['task_id']))
            lat = float(kwargs['lat'])
            lon = float(kwargs['lon'])
            updated = False
            _logger.warning(f'------------------{task.id}')
            if task.status:
                if task.status == 'progress':
                    updated_id = task.write({'status': 'done', 'check_out_latitude': lat, 'check_out_longitude': lon})
                else:
                    updated_id = task.write({'status': 'progress', 'check_in_latitude': lat, 'check_in_longitude': lon})
            else:
                updated_id = task.write({'status': 'progress'})

            if updated_id:
                updated = True

            if updated:
                value = 'Successfully'
            else:
                value = 'Failed to'

            msg = json.dumps({'result': updated, 'data': value},
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/route/plan/employees', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_team_employees(self, **kwargs):
        try:
            _logger.warning(f' ============== ' + str(kwargs['empl']) + ' -- ' + str(kwargs['unauthorize']))
            employee = request.env['hr.employee'].sudo().search([('id', '=', request.em_id)])
            employees = self.get_subordinates(employee)

            my_customers = []
            customers1 = request.env['res.partner'].sudo().search([('responsible', '=', employee.id)])
            for customer1 in customers1:
                customer_dict1 = {}
                customer_dict1['id'] = customer1.id
                customer_dict1['name'] = customer1.name
                customer_dict1['code'] = customer1.code
                my_customers.append(customer_dict1)

            sub_tree = [
                {'id': employee.id, 'name': employee.name, 'customers': my_customers}]
            for record in employees:
                employee_dict = {}
                employee_dict['id'] = record.id
                employee_dict['name'] = record.name
                customer_list = []
                customers = request.env['res.partner'].sudo().search([('responsible', '=', record.id)])
                for customer in customers:
                    customer_dict = {}
                    customer_dict['id'] = customer.id
                    customer_dict['name'] = customer.name
                    customer_dict['code'] = customer.code
                    customer_list.append(customer_dict)
                employee_dict['customers'] = customer_list
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

    # @tools.security.protected_rafiul()
    # @http.route('/web/sales/force/returnable/order/detail', auth='none', type='http', csrf=False, methods=['POST'])
    # def get_returnable_order_detail(self, **kwargs):
    #     try:
    #
    #         returnable_order = request.env['sale.order'].sudo().browse(int(kwargs["order_id"]))
    #
    #         pickings = []
    #         for picking in returnable_order.picking_ids:
    #             if picking.picking_type_id.code == 'outgoing':
    #                 picking_dict = {}
    #                 picking_dict['id'] = picking.id
    #                 picking_dict['name'] = picking.name
    #                 picking_dict['customer_id'] = picking.partner_id.id
    #                 picking_dict['customer'] = picking.partner_id.name
    #                 picking_dict['from_location_id'] = picking.location_id.id
    #                 picking_dict['from_location_name'] = picking.location_id.name
    #                 picking_dict['dest_location_id'] = picking.location_dest_id.id
    #                 picking_dict['dest_location_name'] = picking.location_dest_id.name
    #                 picking_dict['sale_type'] = picking.sale_type
    #                 picking_dict['document'] = picking.origin
    #                 # move_lines = []
    #                 # for line in picking.move_line_ids_without_package:
    #                 #     move_line_dict = {}
    #                 #     move_line_dict['product_id'] = line.product_id.id
    #                 #     move_line_dict['product_name'] = line.product_id.name
    #                 #     move_line_dict['quantity'] = line.qty_done
    #                 #     move_lines.append(move_line_dict)
    #                 # picking_dict['move_lines'] = move_lines
    #
    #                 returnPicking = request.env['stock.return.picking'].sudo().browse(picking.id)
    #                 move_lines = []
    #                 # for move_line in returnPicking.product_return_moves:
    #                 for stock_move in picking.move_lines:
    #                     quantity = stock_move.product_qty
    #                     for move in stock_move.move_dest_ids:
    #                         if move.origin_returned_move_id and move.origin_returned_move_id != stock_move:
    #                             continue
    #                         if move.state in ('partially_available', 'assigned'):
    #                             quantity -= sum(move.move_line_ids.mapped('product_qty'))
    #                         elif move.state in ('done'):
    #                             quantity -= move.product_qty
    #                     quantity = float_round(quantity, precision_rounding=stock_move.product_id.uom_id.rounding)
    #                     move_line_dict = {}
    #                     move_line_dict['product_id'] = stock_move.product_id.id
    #                     move_line_dict['move_id'] = stock_move.id
    #                     move_line_dict['product_name'] = stock_move.product_id.name
    #                     move_line_dict['quantity'] = quantity
    #                     move_lines.append(move_line_dict)
    #                 picking_dict['move_lines'] = move_lines
    #
    #                 pickings.append(picking_dict)
    #
    #         return_details = {
    #             'name': returnable_order.name,
    #             'id': returnable_order.id,
    #             'customer_id': returnable_order.partner_id.id,
    #             'customer': returnable_order.partner_id.name,
    #             'customer_code': returnable_order.partner_id.code,
    #             'delivery_pickings': pickings
    #         }
    #
    #         msg = json.dumps(return_details,
    #                          sort_keys=True, indent=4, cls=ResponseEncoder)
    #         return Response(msg, content_type='application/json;charset=utf-8', status=200)
    #
    #     except Exception as e:
    #         err = {'error': str(e)}
    #         error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
    #         return Response(error, content_type='application/json;charset=utf-8', status=200)
