# -*- coding: utf-8 -*-

from odoo import models, fields, api

class SalesPerformReport(models.AbstractModel):
    _name = 'report.sale_report_extend.sales_value_perform_report_template'

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

        domain = [
            ('is_enable_sales_force', '=', True),
         ]

        if designation:
            domain.append(('type', '=', designation))
        if employee_ids:
            domain.append(('id', 'in', employee_ids))
        if department_id:
            domain.append(('department_id', '=', department_id))

        employees = self.env['hr.employee'].search(domain)
        emp_list = []
        for emp in employees:
            target_lines =[]
            target = 0
            achievement = 0
            shortfall = 0
            child_so = self.env['hr.employee'].search([('id', 'child_of', emp.id)])

            target_lines = self.env['target.history'].search([('emp_id','=', emp.id),('create_date', '>=', date_start),
                                                              ('create_date', '<=', date_end)])
            target = sum(target_lines.mapped('target'))
            if emp.type == 'so':
                current_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', emp.id), ('date', '>=', date_start), ('date', '<=', date_end),
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
                        [('responsible_id', '=', so.id), ('date', '>=', date_start), ('date', '<=', date_end),
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
                'designation' : emp.type,
                'sale_chanel' : emp.department_id.name,
                'target' : target,
                'achievement' : achievement,
                'ach_percent' : ach_percent,
                'short_percent': short_percent,
                'shortfall': shortfall

            })

        return {
            'docs': docs,
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'emp_list': emp_list,
            'designation' : designation,
            'date_start' : date_start,
            'date_end' : date_end,
            'department_name': department_name

        }











