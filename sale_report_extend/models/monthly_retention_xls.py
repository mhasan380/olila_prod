# -*- coding: utf-8 -*-
import base64
import io
from datetime import date, datetime
from odoo import models, fields, api

class CustomerRetentionReportXLS(models.AbstractModel):
    _name = 'report.sale_report_extend.report_customer_retention_xls'
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
        sheet.merge_range(1, 1, 2, 6, 'Month on Month Comparison Report', format0)
        sheet.merge_range(4, 0, 4, 1, 'From Date:  '+ data['from_date'], format11)
        sheet.merge_range(4, 5, 4, 6, 'To Date:  ' + data['to_date'], format11)
        sheet.write(row, col, 'NAME', format21)
        sheet.write(row, col + 1, 'DESIGNATION', format21)
        sheet.write(row, col + 2, 'Last Month Order from No. of Customer', format21)
        sheet.write(row, col + 3, 'MTD Repete Order from No. of Customer', format21)
        sheet.write(row, col + 4, 'Customer Retention %', format21)


        for emp in data['emp_list']:
            row+=1
            sheet.write(row, col, emp['employee_name'], font_size_8)
            sheet.write(row, col + 1, emp['designation'], font_size_8)
            sheet.write(row, col + 2, emp['last_outlet'], font_size_8)
            sheet.write(row, col + 3, emp['repeat_customer'], font_size_8)
            sheet.write(row, col + 4, emp['retention_percent'], font_size_8)





