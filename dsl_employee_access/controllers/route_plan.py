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


class RoutePlanV1APIs(http.Controller):

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
                plan_dict['type'] = route_plan.route_type
                plan_dict['assigned_by'] = route_plan.assigned_by.name
                plan_dict['assigned_to'] = route_plan.assigned_to.name
                # tasks = []
                # for task in route_plan.info_checklist:
                #     task_dict = {}
                #     task_dict['id'] = task.id
                #     task_dict['name'] = task.name_work
                #     task_dict['customer_id'] = task.customer.id
                #     task_dict['customer'] = task.customer.name
                #     task_dict['status'] = task.status
                #     tasks.append(task_dict)
                # plan_dict['tasks'] = tasks
                records.append(plan_dict)

            msg = json.dumps(records,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_rp_01',
                                                 trace_ref=str(e), with_location=False)
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
            type = data_in_json['type']
            master_routes = data_in_json['routes']

            if type == 'secondary':
                customer_model = 'customer.secondary'
                customer_field = 'secondary_customer'
            else:
                customer_model = 'res.partner'
                customer_field = 'customer'

            task_lines = []
            for line in tasks:
                customer = request.env[customer_model].sudo().search([('id', '=', line['customer_id'])])
                if customer:
                    task_line_dict = {
                        'name_work': line['task_name'],
                        customer_field: customer.id,
                    }
                    task_lines.append((0, 0, task_line_dict))
            m_routes = []
            for m_route in master_routes:
                single_m_route = request.env['route.master'].sudo().search([('id', '=', m_route['id'])])
                m_routes.append((4, single_m_route.id))

            vals = {
                'name': plan_name,
                'assigned_to': assigned_to.id,
                'assigned_by': assigned_by.id,
                'sales_plan_date': start_date,
                'end_plan_date': end_date,
                # 'info_checklist': task_lines,
                'route_type': type,
                'route_ids': m_routes
            }

            route_plan_id = request.env['sales.person.plan'].sudo().create(vals)
            route_plan_id.on_change_route_ids()
            route_plan_id.info_checklist.unlink()
            route_plan_id.write({'info_checklist': task_lines})

            order_details = {
                'id': route_plan_id.id,
                'name': route_plan_id.name
            }

            msg = json.dumps(order_details,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_rp_02',
                                                 trace_ref=str(e), with_location=False)
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
            plan_dict['type'] = route_plan.route_type
            plan_dict['end_date'] = route_plan.end_plan_date
            plan_dict['progress'] = route_plan.progress_rate
            plan_dict['assigned_by'] = route_plan.assigned_by.name
            plan_dict['assigned_to'] = route_plan.assigned_to.name
            tasks = []
            for task in route_plan.info_checklist:
                task_dict = {}
                task_dict['id'] = task.id
                task_dict['name'] = task.name_work
                task_dict['responsible'] = route_plan.assigned_to.id
                task_dict['manager'] = route_plan.assigned_by.id
                if route_plan.route_type == 'secondary':
                    task_dict['customer_id'] = task.secondary_customer.id
                    task_dict['customer'] = task.secondary_customer.name
                else:
                    task_dict['customer_id'] = task.customer.id
                    task_dict['customer'] = task.customer.name
                task_dict['remark'] = task.remarks
                task_dict['reason'] = task.incomplete_reason
                task_dict['status'] = task.status
                tasks.append(task_dict)
            routes = []
            for r_route in route_plan.route_ids:
                routes.append(r_route.name)
            plan_dict['routes'] = routes
            regions = []
            for r_region in route_plan.zone_ids:
                regions.append(r_region.name)
            plan_dict['regions'] = regions
            territories = []
            for r_territory in route_plan.territory_ids:
                territories.append(r_territory.name)
            plan_dict['territories'] = territories
            so_markets = []
            for so_market in route_plan.area_ids:
                so_markets.append(so_market.name)
            plan_dict['so_markets'] = so_markets

            plan_dict['tasks'] = tasks

            msg = json.dumps(plan_dict,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_rp_03',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/route/plan/task_update', auth='none', type='http', csrf=False, methods=['POST'])
    def route_plan_task_update(self, **kwargs):
        try:

            task = request.env['rode.list'].sudo().browse(int(kwargs['task_id']))
            lat = kwargs['lat']
            lon = kwargs['lon']
            state = kwargs['status']
            incomplete_reason = kwargs['reason']
            remark = kwargs['remark']

            # if state == 'start':
            #     state = 'progress'

            updated = False

            if state == 'start':
                updated_id = task.write({'status': 'progress', 'check_in_latitude': lat, 'check_in_longitude': lon})
            else:
                updated_id = task.write({'status': state, 'check_out_latitude': lat, 'check_out_longitude': lon,
                                         'incomplete_reason': incomplete_reason, 'remarks': remark})
            # _logger.warning(f'------------------{task.id}')
            # if task.status:
            #     _logger.warning(f'location------------------{lat}, {lon}')
            #     if task.status == 'progress':
            #         updated_id = task.write({'status': 'done', 'check_out_latitude': lat, 'check_out_longitude': lon})
            #     else:
            #         updated_id = task.write({'status': 'progress', 'check_in_latitude': lat, 'check_in_longitude': lon})
            # else:
            #     updated_id = task.write({'status': 'progress'})

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
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_rp_04',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    @tools.security.protected_rafiul()
    @http.route('/web/sales/force/route/plan/employees', website=True, auth='none', type='http', csrf=False,
                methods=['GET'])
    def get_team_employees(self, **kwargs):
        try:
            # _logger.warning(f' ============== ' + str(kwargs['empl']) + ' -- ' + str(kwargs['unauthorize']))
            employee = request.env['hr.employee'].sudo().search([('id', '=', request.em_id)])
            employees = self.get_subordinates(employee)

            my_customers = []

            # adding own primary customers
            customers1 = request.env['res.partner'].sudo().search([('responsible', '=', employee.id)])
            for customer1 in customers1:
                reference_code1 = customer1.code
                if reference_code1 and '/' in reference_code1:
                    x = reference_code1.split('/')[1:]
                    reference_code1 = x[0]
                customer_dict1 = {}
                customer_dict1['id'] = customer1.id
                customer_dict1['name'] = customer1.name
                customer_dict1['code'] = customer1.code
                customer_dict1['type'] = 'primary'
                customer_dict1['reference_code'] = reference_code1
                my_customers.append(customer_dict1)

            # adding own secondary customers
            s_customers1 = request.env['customer.secondary'].sudo().search([('responsible_id', '=', employee.id)])
            for s_customer1 in s_customers1:
                sc_reference_code1 = s_customer1.outlet_code
                if sc_reference_code1 and '/' in sc_reference_code1:
                    x = sc_reference_code1.split('/')[1:]
                    if len(x) > 1:
                        sc_reference_code1 = x[1]
                    else:
                        sc_reference_code1 = x[0]
                s_customer_dict1 = {}
                s_customer_dict1['id'] = s_customer1.id
                s_customer_dict1['name'] = s_customer1.name
                s_customer_dict1['code'] = s_customer1.outlet_code
                s_customer_dict1['type'] = 'secondary'
                s_customer_dict1['reference_code'] = sc_reference_code1
                my_customers.append(s_customer_dict1)

            sub_tree = [
                {'id': employee.id, 'name': employee.name, 'customers': my_customers}]

            # adding subordinates primary & secondary customers
            for record in employees:
                employee_dict = {}
                employee_dict['id'] = record.id
                employee_dict['name'] = record.name
                customer_list = []
                customers = request.env['res.partner'].sudo().search([('responsible', '=', record.id)])
                for customer in customers:
                    reference_code = customer.code
                    if reference_code and '/' in reference_code:
                        x = reference_code.split('/')[1:]
                        reference_code = x[0]
                    customer_dict = {}
                    customer_dict['id'] = customer.id
                    customer_dict['name'] = customer.name
                    customer_dict['code'] = customer.code
                    customer_dict['type'] = 'primary'
                    customer_dict['reference_code'] = reference_code
                    customer_list.append(customer_dict)
                secondary_customers = request.env['customer.secondary'].sudo().search(
                    [('responsible_id', '=', record.id)])
                for s_customer in secondary_customers:
                    sc_reference_code = s_customer.outlet_code
                    if sc_reference_code and '/' in sc_reference_code:
                        x = sc_reference_code.split('/')[1:]
                        if len(x) > 1:
                            sc_reference_code = x[1]
                        else:
                            sc_reference_code = x[0]
                    s_customer_dict = {}
                    s_customer_dict['id'] = s_customer.id
                    s_customer_dict['name'] = s_customer.name
                    s_customer_dict['code'] = s_customer.outlet_code
                    s_customer_dict['type'] = 'secondary'
                    s_customer_dict['reference_code'] = sc_reference_code
                    customer_list.append(s_customer_dict)
                employee_dict['customers'] = customer_list
                sub_tree.append(employee_dict)

            msg = json.dumps(sub_tree,
                             sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(msg, content_type='application/json;charset=utf-8', status=200)

        except Exception as e:
            err = {'error': str(e)}
            tools.security.create_log_salesforce(http.request, access_type='protected', system_returns='exc_rp_05',
                                                 trace_ref=str(e), with_location=False)
            error = json.dumps(err, sort_keys=True, indent=4, cls=ResponseEncoder)
            return Response(error, content_type='application/json;charset=utf-8', status=200)

    def get_subordinates(self, employee):
        subordinate_list = []
        subordinates = request.env['hr.employee'].sudo().search(
            [('parent_id', '=', employee.id), '|', ('active', '=', True), ('active', '=', False)])
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
