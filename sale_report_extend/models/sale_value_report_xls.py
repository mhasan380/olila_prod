# -*- coding: utf-8 -*-
import base64
import io
from odoo import models, fields, api

class SalesPerformReportXLS(models.AbstractModel):
    _name = 'report.sale_report_extend.report_sale_value_perform_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, patients):
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
        sheet.merge_range(1, 1, 2, 6, 'Sales Personnel Wise Value Performance Report', format0)
        sheet.merge_range(4, 0, 4, 1, 'From Date:  '+ data['from_date'], format11)
        sheet.merge_range(4, 5, 4, 6, 'To Date:  ' + data['to_date'], format11)
        sheet.write(row, col, 'NAME', format21)
        sheet.write(row, col + 1, 'DESIGNATION', format21)
        sheet.write(row, col + 2, 'SALES CHANEL', format21)
        sheet.write(row, col + 3, 'TEAM MEMEBER', format21)
        sheet.write(row, col + 4, 'TARGET', format21)
        sheet.write(row, col + 5, 'MTD ACH.', format21)
        sheet.write(row, col + 6, 'ACHIEVEMENT %', format21)
        sheet.write(row, col + 7, 'SHORTFALL/SURPLUS', format21)
        sheet.write(row, col + 8, 'SHORTFALL/SURPLUS %', format21)

        for emp in data['emp_list']:
            row+=1
            sheet.write(row, col, emp['employee_name'], font_size_8)
            sheet.write(row, col + 1, emp['designation'], font_size_8)
            sheet.write(row, col + 2, emp['sale_chanel'], font_size_8)
            sheet.write(row, col + 3, emp['so_number'], font_size_8)
            sheet.write(row, col + 4, emp['target'], font_size_8_r)
            sheet.write(row, col + 5, emp['achievement'], font_size_8_r)
            sheet.write(row, col + 6, emp['ach_percent'], font_size_8)
            sheet.write(row, col + 7, emp['shortfall'], font_size_8_r)
            sheet.write(row, col + 8, emp['short_percent'], font_size_8)


        # for obj in patients:
        #     sheet = workbook.add_worksheet(obj.name)
        #     row = 3
        #     col = 3
        #     sheet.set_column('D:D', 12)
        #     sheet.set_column('E:E', 13)
        #
        #     row += 1
        #     sheet.merge_range(row, col, row, col + 1, 'ID Card', format_1)
        #
        #     row += 1
        #     if obj.image:
        #         patient_image = io.BytesIO(base64.b64decode(obj.image))
        #         sheet.insert_image(row, col, "image.png", {'image_data': patient_image, 'x_scale': 0.5, 'y_scale': 0.5})
        #
        #         row += 6
        #     sheet.write(row, col, 'Name', bold)
        #     sheet.write(row, col + 1, obj.name)
        #     row += 1
        #     sheet.write(row, col, 'Age', bold)
        #     sheet.write(row, col + 1, obj.age)
        #     row += 1
        #     sheet.write(row, col, 'Reference', bold)
        #     sheet.write(row, col + 1, obj.reference)
        #
        #     row += 2
        #     sheet.merge_range(row, col, row + 1, col + 1, '', format_1)
