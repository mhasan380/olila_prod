# -*- coding: utf-8 -*-

from odoo import models, fields, api
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
from collections import OrderedDict


class ProductivityPerformanceReport(models.AbstractModel):
    _name = 'report.sale_report_extend.productivity_performance_template'

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
        saleble_products = self.env['product.product'].search_count([('type','=','product'),('sale_ok','=', True),('fs_type','=','master')])
        emp_list = []
        for emp in employees:
            billing_sku = 0
            achievement = 0
            outlet = 0
            unique_sku = 0
            total_order = 0
            total_products = []
            if emp.type == 'so':
                current_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', emp.id), ('date', '>=', date_start), ('date', '<=', date_end),('state', '=', 'posted')])
                achievement = sum(current_pay_ids.mapped('amount'))
                sale_orders = self.env['sale.order'].search(
                    [('responsible', '=', emp.id), ('date_order', '>=', date_start),
                     ('date_order', '<=', date_end), ('state', 'in', ('sale', 'done'))])
                customers = list(OrderedDict.fromkeys(sale_orders.mapped('partner_id')))
                outlet = (len(customers))
                # for order in sale_orders:
                #     billing_sku += len(order.order_line)
                product_lines = self.env['sale.order.line'].search(
                    [('order_id.responsible', '=', emp.id), ('order_id.date_order', '>=', date_start),
                     ('order_id.date_order', '<=', date_end), ('order_id.state', 'in', ('sale', 'done'))])
                billing_sku = len(product_lines)
                products = list(OrderedDict.fromkeys(product_lines.mapped('product_id')))
                unique_sku = len(products)
                total_order = len(sale_orders)
                total_outlets = self.env['res.partner'].search_count([('responsible','=', emp.id),('is_customer','=', True)])

            elif emp.type != 'so':
                child_so = self.env['hr.employee'].sudo().search([('id', 'child_of', emp.id), ('type', '=', 'so'), "|",
                                        ("active", "=", True),
                                        ("active", "=", False)])
                total_outlets = self.env['res.partner'].search_count(
                    [('responsible', 'child_of', emp.id), ('is_customer', '=', True)])

                for so in child_so:
                    current_pay_ids = self.env['account.payment'].search(
                    [('responsible_id', '=', so.id), ('date', '>=', date_start), ('date', '<=', date_end),('state', '=', 'posted')])
                    so_achiement = sum(current_pay_ids.mapped('amount'))
                    achievement += so_achiement
                    sale_orders = self.env['sale.order'].search(
                        [('responsible', '=', so.id), ('date_order', '>=', date_start),
                         ('date_order', '<=', date_end), ('state', 'in', ('sale', 'done'))])
                    customers = list(OrderedDict.fromkeys(sale_orders.mapped('partner_id')))
                    outlet += float((len(customers)))
                    product_lines = self.env['sale.order.line'].search(
                        [('order_id.responsible', '=', so.id), ('order_id.date_order', '>=', date_start),
                         ('order_id.date_order', '<=', date_end), ('order_id.state', 'in', ('sale', 'done'))])
                    billing_sku += float(len(product_lines))
                    total_products += product_lines.mapped('product_id')
                    total_order += float(len(sale_orders))
                products = list(OrderedDict.fromkeys(total_products))
                unique_sku = float(len(products))

            if total_order > 0:
                lpc = billing_sku / total_order
                order_value = achievement / total_order
            else:
                lpc = 0
                order_value = 0
            assortment = unique_sku
            if assortment > 0:
                assort = float(assortment/saleble_products) * 100
                assort_percent = ('{:.2f} %').format(float(assort))
            else:
                assort_percent = 0
            if outlet > 0:
                productivity = float(outlet/total_outlets) * 100
                productivity_percent = ('{:.2f} %').format(float(productivity))
            else:
                productivity_percent = 0

            emp_list.append({
                'employee_name': emp.name,
                'designation': emp.type,
                'achievement': achievement,
                'outlet': outlet,
                'total_outlets' : total_outlets,
                'productivity_percent' : productivity_percent,
                'billing_sku' : billing_sku,
                'total_order': total_order,
                'lpc': lpc,
                'order_value': order_value,
                'unique_sku' : unique_sku,
                'assortment' : assortment,
                'assort_percent' : assort_percent


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











