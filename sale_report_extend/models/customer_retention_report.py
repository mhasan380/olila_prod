# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_repr
import calendar
from collections import OrderedDict


class CustomerRetentionReport(models.AbstractModel):
    _name = 'report.sale_report_extend.customer_retention_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        employee_ids = data['form']['employee_ids']
        designation = data['form']['designation']
        date_start = data['form']['from_date']
        date_end = data['form']['to_date']
        department_id = data['form']['department_id']
        department_name = self.env['hr.employee'].search([('id','=', department_id)])

        input_month = datetime.strptime(date_start, "%Y-%m-%d").month
        input_year = datetime.strptime(date_start, "%Y-%m-%d").year
        last_start_day = fields.Date.today().replace(day=1, month=(int(input_month) - 1), year=int(input_year) )
        month_range = calendar.monthrange(int(input_year), int(input_month))
        last_end_day = fields.Date.today().replace(day=month_range[1], month=(int(input_month) - 1), year=int(input_year))

        domain = [
            ('is_enable_sales_force', '=', True)
         ]

        if designation:
            domain.append(('type', '=', designation))
        if employee_ids:
            domain.append(('id', 'in', employee_ids))
        if department_id:
            domain.append(('department_id', '=', department_id))

        employees = self.env['hr.employee'].sudo().search(domain)
        emp_list = []
        for emp in employees:
            child_emp = self.env['hr.employee'].search([('parent_id', '=', emp.id)])
            team_member = float(len(child_emp))
            repeat_customer = 0
            total_customer = []
            last_total_customer = []

            if emp.type == 'so':
                sale_orders = self.env['sale.order'].search(
                    [('responsible', '=', emp.id), ('date_order', '>=', date_start),
                     ('date_order', '<=', date_end), ('state', 'in', ('sale', 'done'))])
                current_customers = list(OrderedDict.fromkeys(sale_orders.mapped('partner_id')))
                last_sale_orders = self.env['sale.order'].search(
                    [('responsible', '=', emp.id), ('date_order', '>=', last_start_day),
                     ('date_order', '<=', last_end_day), ('state', 'in', ('sale', 'done'))])
                last_customers = list(OrderedDict.fromkeys(last_sale_orders.mapped('partner_id')))
                last_outlet = len(last_customers)
                for customer in current_customers:
                    if customer in last_customers:
                        repeat_customer += 1


            elif emp.type != 'so':
                child_so = self.env['hr.employee'].sudo().search([('id', 'child_of', emp.id), ('type', '=', 'so'), "|",
                                        ("active", "=", True),
                                        ("active", "=", False),])
                for so in child_so:
                    sale_orders = self.env['sale.order'].search(
                        [('responsible', '=', so.id), ('date_order', '>=', date_start),
                         ('date_order', '<=', date_end), ('state', 'in', ('sale', 'done'))])
                    total_customer += sale_orders.mapped('partner_id')
                    last_sale_orders = self.env['sale.order'].search(
                        [('responsible', '=', so.id), ('date_order', '>=', last_start_day),
                         ('date_order', '<=', last_end_day), ('state', 'in', ('sale', 'done'))])
                    last_total_customer += last_sale_orders.mapped('partner_id')
                current_customers = list(OrderedDict.fromkeys(total_customer))
                last_customers = list(OrderedDict.fromkeys(last_total_customer))
                for customer in current_customers:
                    if customer in last_customers:
                        repeat_customer += 1
                last_outlet = len(last_customers)

            if last_outlet > 0:
                retention = float(repeat_customer / last_outlet) * 100
                retention_percent = ('{:.2f} %').format(float(retention))
            else:
                retention_percent = 0

            emp_list.append({
                'employee_name': emp.name,
                'designation': emp.type,
                'last_outlet' : last_outlet,
                'repeat_customer' : repeat_customer,
                'retention_percent' : retention_percent

            })

        return {
            'docs': docs,
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'emp_list': emp_list,
            'designation': designation,
            'date_start': date_start,
            'date_end': date_end,
            'department_name': department_name

        }











