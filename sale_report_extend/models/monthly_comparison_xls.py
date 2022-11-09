# -*- coding: utf-8 -*-
import base64
import io
from datetime import date, datetime
from odoo import models, fields, api

class MonthlyComparisonReportXLS(models.AbstractModel):
    _name = 'report.sale_report_extend.report_sale_monthly_comparison_xls'
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
        sheet.set_column('L:L', 18)
        sheet.merge_range(1, 1, 2, 6, 'Month on Month Comparison Report', format0)
        sheet.merge_range(4, 0, 4, 1, 'From Date:  '+ data['from_date'], format11)
        sheet.merge_range(4, 5, 4, 6, 'To Date:  ' + data['to_date'], format11)
        sheet.write(row, col, 'NAME', format21)
        sheet.write(row, col + 1, 'DESIGNATION', format21)
        sheet.write(row, col + 2, 'TOTAL DAYS', format21)
        sheet.write(row, col + 3, 'PASSED DAYS', format21)
        sheet.write(row, col + 4, 'REMAINING DAYS', format21)
        sheet.write(row, col + 5, 'TARGET', format21)
        sheet.write(row, col + 6, 'MTD ACH.', format21)
        sheet.write(row, col + 7, 'MTD AVG. DAILY SALES', format21)
        sheet.write(row, col + 8, 'REQ. AVG. DAILY SALES', format21)
        sheet.write(row, col + 9, 'PRODUCTIVITY/SALES PERSONNEL', format21)
        sheet.write(row, col + 10, 'LAST MONTH ACH.', format21)
        sheet.write(row, col + 11, 'MONTH ON MONTH GROWTH %', format21)

        for emp in data['emp_list']:
            row+=1
            sheet.write(row, col, emp['employee_name'], font_size_8)
            sheet.write(row, col + 1, emp['designation'], font_size_8)
            sheet.write(row, col + 2, emp['total_bank_day'], font_size_8)
            sheet.write(row, col + 3, emp['passed_bank_day'], font_size_8)
            sheet.write(row, col + 4, emp['remain_days'], font_size_8_r)
            sheet.write(row, col + 5, emp['target'], font_size_8_r)
            sheet.write(row, col + 6, emp['achievement'], font_size_8)
            sheet.write(row, col + 7, emp['mtd_avg_sale'], font_size_8_r)
            sheet.write(row, col + 8, emp['req_avg_sale'], font_size_8)
            sheet.write(row, col + 9, emp['productivity'], font_size_8)
            sheet.write(row, col + 10, emp['last_achivement'], font_size_8)
            sheet.write(row, col + 11, emp['growth_percent'], font_size_8)




