import time
from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class SalesValuePerformance(models.TransientModel):
    _name = "sales.value.performance"
    _description = "Sales Value Performance Report Wizard"

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

    def get_pdf_report(self):

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'employee_ids': self.employee_ids.ids,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'designation': self.designation,
                'department_id' : self.department_id.id
            },
        }

        return self.env.ref('sale_report_extend.sales_value_perform_report').report_action(self, data=data)
    def get_xls_report(self):
        domain = [
            ('is_enable_sales_force', '=', True),
        ]

        if self.designation:
            domain.append(('type', '=', self.designation))
        if self.employee_ids:
            domain.append(('id', 'in', self.employee_ids.ids))
        if self.department_id:
            domain.append(('department_id', '=', self.department_id.id))

        employees = self.env['hr.employee'].search(domain)
        emp_list = []
        for emp in employees:
            target_lines = []
            target = 0
            achievement = 0
            shortfall = 0
            child_emp = self.env['hr.employee'].search([('parent_id', '=', emp.id)])

            target_lines = self.env['target.history'].search(
                [('emp_id', '=', emp.id), ('create_date', '>=', self.from_date),
                 ('create_date', '<=', self.to_date)])
            target = sum(target_lines.mapped('target'))
            if emp.type == 'so':
                current_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', emp.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date),
                     ('state', '=', 'posted')])
                achievement = sum(current_pay_ids.mapped('amount'))


            elif emp.type != 'so':
                child_so = self.env['hr.employee'].sudo().search([('id', 'child_of', emp.id), ('type', '=', 'so'), "|",
                                                                  ("active", "=", True),
                                                                  ("active", "=", False), ])
                so_achiement = 0
                so_last = 0
                for so in child_so:
                    current_pay_ids = self.env['account.payment'].search(
                        [('responsible_id', '=', so.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date),
                         ('state', '=', 'posted')])
                    so_achiement = sum(current_pay_ids.mapped('amount'))
                    achievement += so_achiement
            if target > 0:
                percent = float(achievement / target) * 100
                ach_percent = ('{:.2f} %').format(float(percent))
            else:
                ach_percent = 0

            shortfall = target - achievement
            if target > 0:
                short = float(shortfall / target) * 100
                short_percent = ('{:.2f} %').format(float(short))
            else:
                short_percent = 0

            emp_list.append({
                'employee_name': emp.name,
                'designation': emp.type,
                'sale_chanel': emp.department_id.name,
                'target': ('{:,.2f}').format(float(target)),
                'achievement': ('{:,.2f}').format(float(achievement)),
                'ach_percent': ach_percent,
                'short_percent': short_percent,
                'shortfall': ('{:,.2f}').format(float(shortfall)),
                'so_number': len(child_emp)

            })
        data = {

                'employee_ids': self.employee_ids,
                'emp_list' : emp_list,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'designation': self.designation,
                'department_id' : self.department_id,


        }

        return self.env.ref('sale_report_extend.report_sale_value_perform_xlsx').report_action(self, data=data)
    # Name will be module_name.report_action_id
