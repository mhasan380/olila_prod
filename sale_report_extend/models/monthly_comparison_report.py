# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, date, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from odoo.tools import float_repr
import calendar


class MonthlyComparisonReport(models.AbstractModel):
    _name = 'report.sale_report_extend.monthly_comparison_report_template'

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
        total_bank_day = data['form']['total_bank_day']
        passed_bank_day = data['form']['passed_bank_day']

        remain_days = total_bank_day - passed_bank_day


        input_month = datetime.strptime(date_start, "%Y-%m-%d").month
        input_year = datetime.strptime(date_start, "%Y-%m-%d").year
        last_start_day_str = datetime.strptime(date_start, "%Y-%m-%d") + relativedelta(months=-1)
        last_end_day_str = datetime.strptime(date_end, "%Y-%m-%d") + relativedelta(months=-1)
        last_start_day = datetime.strftime(last_start_day_str, "%Y-%m-%d")
        last_end_day = datetime.strftime(last_end_day_str, "%Y-%m-%d")
        print(last_start_day)

        domain = [
            ('is_enable_sales_force', '=', True),  "|",
        ("active", "=", True),
        ("active", "=", False),
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
            target_lines = []
            target = 0
            achievement = 0
            shortfall = 0
            last_achivement = 0
            child_emp = self.env['hr.employee'].search([('parent_id', '=', emp.id)])
            team_member = float(len(child_emp))

            target_lines = emp.history_lines.filtered(lambda x: x.month == str(input_month) and x.year == str(input_year))
            target = sum(target_lines.mapped('target'))
            if emp.type == 'so':
                current_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', emp.id), ('date', '>=', date_start), ('date', '<=', date_end),('state', '=', 'posted')])
                achievement = sum(current_pay_ids.mapped('amount'))
                last_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', emp.id), ('date', '>=', last_start_day), ('date', '<=', last_end_day),('state', '=', 'posted')])
                last_achivement = sum(last_pay_ids.mapped('amount'))

            elif emp.type != 'so':
                child_so = self.env['hr.employee'].sudo().search([('id', 'child_of', emp.id), ('type', '=', 'so'), "|",
                                        ("active", "=", True),
                                        ("active", "=", False),])
                so_achiement = 0
                so_last = 0
                for so in child_so:
                    current_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', so.id), ('date', '>=', date_start), ('date', '<=', date_end),('state', '=', 'posted')])
                    so_achiement = sum(current_pay_ids.mapped('amount'))
                    last_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', so.id), ('date', '>=', last_start_day), ('date', '<=', last_end_day),('state', '=', 'posted')])
                    so_last = sum(last_pay_ids.mapped('amount'))
                    achievement += so_achiement
                    last_achivement += so_last
            print(last_achivement)

            shortfall = target - achievement
            mtd_avg_sale = achievement / passed_bank_day
            req_avg_sale = shortfall / remain_days
            if team_member > 0:
                productivity = achievement / team_member
            else:
                productivity = achievement

            if last_achivement > 0:
                growth = float( (achievement - last_achivement) / last_achivement) * 100
                growth_percent = ('{:.2f} %').format(float(growth))
            else:
                growth_percent = 0


            emp_list.append({
                'employee_name': emp.name,
                'designation': emp.type,
                'total_bank_day': total_bank_day,
                'passed_bank_day': passed_bank_day,
                'remain_days': remain_days,
                'target': target,
                'achievement': achievement,
                'mtd_avg_sale' : mtd_avg_sale,
                'req_avg_sale' : req_avg_sale,
                'productivity' : productivity,
                'last_achivement': last_achivement,
                'growth_percent': growth_percent,

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











