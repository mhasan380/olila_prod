import time
from datetime import date, datetime
import pytz
import json
import datetime
import io
from odoo import api, fields, models, _
from odoo.tools import date_utils
from dateutil.relativedelta import relativedelta
from collections import OrderedDict
from odoo.exceptions import ValidationError
try:
    from odoo.tools.misc import xlsxwriter
except ImportError:
    import xlsxwriter

class ProductivePerformanceWizard(models.TransientModel):
    _name = "productive.performance.wizard"
    _description = "Productivity Performance Wizard"

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

        return self.env.ref('sale_report_extend.productivity_performance_report').report_action(self, data=data)
    def get_xls_report(self):
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
        saleble_products = self.env['product.product'].search_count(
            [('type', '=', 'product'), ('sale_ok', '=', True), ('fs_type', '=', 'master')])
        emp_list = []
        for emp in employees:
            billing_sku = 0
            achievement = 0
            outlet = 0
            unique_sku = 0
            total_order = 0
            total_products = []
            total_sales_order = []
            if emp.type == 'so':
                current_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', emp.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date),
                     ('state', '=', 'posted')])
                achievement = sum(current_pay_ids.mapped('amount'))
                sale_orders = self.env['sale.order'].search(
                    [('responsible', '=', emp.id), ('date_order', '>=', self.from_date),
                     ('date_order', '<=', self.to_date), ('state', 'in', ('sale', 'done'))])
                customers = list(OrderedDict.fromkeys(sale_orders.mapped('partner_id')))
                outlet = (len(customers))
                # for order in sale_orders:
                #     billing_sku += len(order.order_line)
                product_lines = self.env['sale.order.line'].search(
                    [('order_id.responsible', '=', emp.id), ('order_id.date_order', '>=',self.from_date),
                     ('order_id.date_order', '<=', self.to_date), ('order_id.state', 'in', ('sale', 'done'))])
                billing_sku = len(product_lines)
                products = list(OrderedDict.fromkeys(product_lines.mapped('product_id')))
                unique_sku = len(products)
                total_order = len(sale_orders)
                total_outlets = self.env['res.partner'].search_count(
                    [('responsible', '=', emp.id), ('is_customer', '=', True)])

            elif emp.type != 'so':
                child_so = self.env['hr.employee'].sudo().search([('id', 'child_of', emp.id), ('type', '=', 'so'), "|",
                                                                  ("active", "=", True),
                                                                  ("active", "=", False)])
                total_outlets = self.env['res.partner'].search_count(
                    [('responsible', 'child_of', emp.id), ('is_customer', '=', True)])

                for so in child_so:
                    current_pay_ids = self.env['account.payment'].search(
                        [('responsible_id', '=', so.id), ('date', '>=', self.from_date), ('date', '<=', self.to_date),
                         ('state', '=', 'posted')])
                    so_achiement = sum(current_pay_ids.mapped('amount'))
                    achievement += so_achiement
                    sale_orders = self.env['sale.order'].search(
                        [('responsible', '=', so.id), ('date_order', '>=', self.from_date),
                         ('date_order', '<=', self.to_date), ('state', 'in', ('sale', 'done'))])
                    total_sales_order += sale_orders.mapped('partner_id')
                    product_lines = self.env['sale.order.line'].search(
                        [('order_id.responsible', '=', so.id), ('order_id.date_order', '>=', self.from_date),
                         ('order_id.date_order', '<=', self.to_date), ('order_id.state', 'in', ('sale', 'done'))])
                    billing_sku += float(len(product_lines))
                    total_products += product_lines.mapped('product_id')
                    total_order += float(len(sale_orders))
                products = list(OrderedDict.fromkeys(total_products))
                unique_sku = float(len(products))
                customers = list(OrderedDict.fromkeys(total_sales_order))
                outlet = (len(customers))

            if total_order > 0:
                lpc = billing_sku / total_order
                order_value = achievement / total_order
            else:
                lpc = 0
                order_value = 0
            assortment = unique_sku
            if assortment > 0:
                assort = float(assortment / saleble_products) * 100
                assort_percent = ('{:.2f} %').format(float(assort))
            else:
                assort_percent = 0
            if total_outlets > 0:
                productivity = float(outlet / total_outlets) * 100
                productivity_percent = ('{:.2f} %').format(float(productivity))
            else:
                productivity_percent = 0

            emp_list.append({
                'employee_name': emp.name,
                'designation': emp.type,
                'achievement': achievement,
                'outlet': outlet,
                'total_outlets': total_outlets,
                'productivity_percent': productivity_percent,
                'billing_sku': billing_sku,
                'total_order': total_order,
                'lpc': lpc,
                'order_value': order_value,
                'unique_sku': unique_sku,
                'assortment': assortment,
                'assort_percent': assort_percent

            })

            data = {

                'employee_ids': self.employee_ids,
                'emp_list': emp_list,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'designation': self.designation,
                'department_id': self.department_id,

            }

        return self.env.ref('sale_report_extend.report_productivity_performance_xlsx').report_action(self, data=data)
    # # Name will be module_name.report_action_id
