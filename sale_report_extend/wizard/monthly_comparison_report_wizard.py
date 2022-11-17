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


try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class MonthlyComparisonWizard(models.TransientModel):
    _name = "monthly.comparison.wizard"
    _description = "Month on Month Comparison Report"

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    total_bank_day = fields.Float(string="Total Banking Days")
    passed_bank_day = fields.Float(string="Passed Banking Days")
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

    @api.constrains('total_bank_day')
    def _check_total_bank_day(self):
        for record in self:
            if record.total_bank_day <= 0:
                raise ValidationError(_(
                    "Total Banking day Must be greater than 0"))

    @api.constrains('passed_bank_day')
    def _check_passed_bank_day(self):
        for record in self:
            if record.passed_bank_day <= 0:
                raise ValidationError(_(
                    "Passed Banking day Must be greater than 0"))

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
                'total_bank_day' : self.total_bank_day,
                'passed_bank_day': self.passed_bank_day,
            },
        }

        return self.env.ref('sale_report_extend.monthly_sale_comparison_report').report_action(self, data=data)
    def get_xls_report(self):
        remain_days = self.total_bank_day - self.passed_bank_day

        input_month = self.from_date.month
        input_year = self.from_date.year
        last_start_day_str = self.from_date + relativedelta(months=-1)
        last_end_day_str = self.to_date + relativedelta(months=-1)
        last_start_day = datetime.datetime.strftime(last_start_day_str, "%Y-%m-%d")
        last_end_day = datetime.datetime.strftime(last_end_day_str, "%Y-%m-%d")

        domain = [
            ('is_enable_sales_force', '=', True), "|",
            ("active", "=", True),
            ("active", "=", False),
        ]

        if self.designation:
            domain.append(('type', '=', self.designation))
        if self.employee_ids:
            domain.append(('id', 'in', self.employee_ids.ids))
        if self.department_id:
            domain.append(('department_id', '=', self.department_id.id))

        employees = self.env['hr.employee'].sudo().search(domain)
        emp_list = []
        for emp in employees:
            target_lines = []
            target = 0
            achievement = 0
            shortfall = 0
            last_achivement = 0
            child_emp = self.env['hr.employee'].search([('parent_id', '=', emp.id)])
            team_member = float(len(child_emp))

            target_lines = emp.history_lines.filtered(
                lambda x: x.month == str(input_month) and x.year == str(input_year))
            target = sum(target_lines.mapped('target'))
            if emp.type == 'so':
                current_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', emp.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date),
                     ('state', '=', 'posted')])
                achievement = sum(current_pay_ids.mapped('amount'))
                last_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', emp.id), ('date', '>=', last_start_day), ('date', '<=', last_end_day),
                     ('state', '=', 'posted')])
                last_achivement = sum(last_pay_ids.mapped('amount'))

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
                    last_pay_ids = self.env['account.payment'].search(
                        [('responsible_id', '=', so.id), ('date', '>=', last_start_day), ('date', '<=', last_end_day),
                         ('state', '=', 'posted')])
                    so_last = sum(last_pay_ids.mapped('amount'))
                    achievement += so_achiement
                    last_achivement += so_last

            shortfall = target - achievement
            mtd_avg_sale = achievement / self.passed_bank_day
            req_avg_sale = shortfall / remain_days
            if team_member > 0:
                productivity = achievement / team_member
            else:
                productivity = achievement

            if last_achivement > 0:
                growth = float((achievement - last_achivement) / last_achivement) * 100
                growth_percent = ('{:.2f} %').format(float(growth))
            else:
                growth_percent = 0

            emp_list.append({
                'employee_name': emp.name,
                'designation': emp.type,
                'total_bank_day': self.total_bank_day,
                'passed_bank_day': self.passed_bank_day,
                'remain_days': remain_days,
                'target': target,
                'achievement': achievement,
                'mtd_avg_sale': mtd_avg_sale,
                'req_avg_sale': req_avg_sale,
                'productivity': productivity,
                'last_achivement': last_achivement,
                'growth_percent': growth_percent,

            })
        data = {

                'employee_ids': self.employee_ids,
                'emp_list' : emp_list,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'designation': self.designation,
                'department_id' : self.department_id,


        }

        return self.env.ref('sale_report_extend.report_sale_monthly_comparison_xlsx').report_action(self, data=data)
    # Name will be module_name.report_action_id
