# -*- coding: utf-8 -*-
import base64
import io
from datetime import date, datetime
from odoo import models, fields, api

class ProductivityPerformanceReportXLS(models.AbstractModel):
    _name = 'report.sale_report_extend.report_productivity_performance_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, employees):
        sheet = workbook.add_worksheet('Employee_lines')
        bold = workbook.add_format({'bold': True})
        format_1 = workbook.add_format({'bold': True, 'align': 'center', 'bg_color': 'yellow'})
        format0 = workbook.add_format({'font_size': 20, 'align': 'center', 'bold': True})
        format11 = workbook.add_format({'font_size': 11, 'align': 'left', 'bold': True})
        format21 = workbook.add_format({'font_size': 10, 'align': 'center', 'bold': True,'bg_color': 'yellow'})
        font_size_8 = workbook.add_format({'font_size': 9, 'align': 'center'})
        font_size_8_r = workbook.add_format({'font_size': 9, 'align': 'right'})
        row = 7
        col = 0
        sheet.set_column('A:A', 24)
        sheet.set_column('B:B', 12)
        sheet.set_column('C:C', 12)
        sheet.set_column('D:D', 12)
        sheet.set_column('E:E', 12)
        sheet.set_column('F:F', 12)
        sheet.set_column('G:G', 14)
        sheet.set_column('H:H', 18)
        sheet.set_column('I:I', 18)
        sheet.set_column('J:J', 18)
        sheet.set_column('K:K', 18)
        sheet.merge_range(1, 1, 2, 6, 'Productivity Performance Report', format0)
        sheet.merge_range(4, 0, 4, 1, 'From Date:  '+ data['from_date'], format11)
        sheet.merge_range(4, 5, 4, 6, 'To Date:  ' + data['to_date'], format11)
        sheet.write(row, col, 'NAME', format21)
        sheet.write(row, col + 1, 'DESIGNATION', format21)
        sheet.write(row, col + 2, 'PRODUCTIVE OUTLET', format21)
        sheet.write(row, col + 3, 'PRODUCTIVITY %', format21)
        sheet.write(row, col + 4, 'BILLING SKU', format21)
        sheet.write(row, col + 5, 'SALES ORDER', format21)
        sheet.write(row, col + 6, 'LPC', format21)
        sheet.write(row, col + 7, 'ORDER VALUE/INVOICE', format21)
        sheet.write(row, col + 8, 'UNIQUE SKU', format21)
        sheet.write(row, col + 9, 'PRODUCT ASSORTMENT', format21)
        sheet.write(row, col + 10, 'PRODUCT ASSORTMENT %', format21)

        for emp in data['emp_list']:
            row+=1
            sheet.write(row, col, emp['employee_name'], font_size_8)
            sheet.write(row, col + 1, emp['designation'], font_size_8)
            sheet.write(row, col + 2, emp['outlet'], font_size_8)
            sheet.write(row, col + 3, emp['productivity_percent'], font_size_8)
            sheet.write(row, col + 4, emp['billing_sku'], font_size_8_r)
            sheet.write(row, col + 5, emp['total_order'], font_size_8_r)
            sheet.write(row, col + 6, emp['lpc'], font_size_8)
            sheet.write(row, col + 7, emp['order_value'], font_size_8_r)
            sheet.write(row, col + 8, emp['unique_sku'], font_size_8)
            sheet.write(row, col + 9, emp['assortment'], font_size_8)
            sheet.write(row, col + 10, emp['assort_percent'], font_size_8)





