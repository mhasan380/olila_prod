import time
from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from collections import OrderedDict
import calendar


try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class CustomerRetentionWizard(models.TransientModel):
    _name = "customer.retention.wizard"
    _description = "Customer Retention Performance Report"

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    designation = fields.Selection([
        ('nsm', 'NSM'),
        ('deputy', 'Deputy NSM'),
        ('dsm', 'DSM'),
        ('rsm', 'RSM'),
        ('asm', 'ASM'),
        ('tso', 'TSO'),
        ('so', 'SO'),
    ],  string='Designation')
    employee_ids = fields.Many2many('hr.employee',string="Employee" , domain=[('type','!=', False)])
    department_id = fields.Many2one('hr.department', string="Department", domain=[('name','in', ('Retail Sales', 'Corporate Sales'))])

    @api.constrains('to_date')
    def _check_to_date(self):
        for record in self:
            if record.to_date.month != record.from_date.month:
                raise ValidationError(_(
                    "From and To Date Must be in same month!"))

    def get_pdf_report(self):

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'employee_ids': self.employee_ids.ids,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'designation': self.designation,
                'department_id' : self.department_id.id,
            },
        }

        return self.env.ref('sale_report_extend.customer_retention_report').report_action(self, data=data)
    def get_xls_report(self):
        input_month = self.from_date.month
        input_year = self.from_date.year
        last_start_day = fields.Date.today().replace(day=1, month=(int(input_month) - 1), year=int(input_year))
        month_range = calendar.monthrange(int(input_year), int(input_month))
        last_end_day = fields.Date.today().replace(day=month_range[1], month=(int(input_month) - 1),
                                                   year=int(input_year))

        domain = [
            ('is_enable_sales_force', '=', True)
        ]

        if self.designation:
            domain.append(('type', '=', self.designation.id))
        if self.employee_ids:
            domain.append(('id', 'in', self.employee_ids.ids))
        if self.department_id:
            domain.append(('department_id', '=', self.department_id.id))

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
                    [('responsible', '=', emp.id), ('date_order', '>=', self.from_date),
                     ('date_order', '<=', self.to_date), ('state', 'in', ('sale', 'done'))])
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
                                                                  ("active", "=", False), ])
                for so in child_so:
                    sale_orders = self.env['sale.order'].search(
                        [('responsible', '=', so.id), ('date_order', '>=', self.from_date),
                         ('date_order', '<=', self.to_date), ('state', 'in', ('sale', 'done'))])
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
                'last_outlet': last_outlet,
                'repeat_customer': repeat_customer,
                'retention_percent': retention_percent

            })
        data = {

                'employee_ids': self.employee_ids,
                'emp_list' : emp_list,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'designation': self.designation,
                'department_id' : self.department_id,
        }

        return self.env.ref('sale_report_extend.report_customer_retention_xlsx').report_action(self, data=data)
    # Name will be module_name.report_action_id
