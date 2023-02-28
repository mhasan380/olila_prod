# -*- coding: utf-8 -*-
import base64
import io
from datetime import date, datetime
from odoo import models, fields, api

class InterTransferReportXLS(models.AbstractModel):
    _name = 'report.internal_transfer_summary_report.transfer_sum_xls'
    _inherit = 'report.report_xlsx.abstract'

    def generate_xlsx_report(self, workbook, data, products):
        sheet = workbook.add_worksheet('Product_lines')
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
        sheet.merge_range(1, 1, 2, 6, 'Inter Transfer Report(ProductWise)', format0)
        sheet.merge_range(4, 0, 4, 1, 'From Date:  '+ data['from_date'], format11)
        sheet.merge_range(4, 5, 4, 6, 'To Date:  ' + data['to_date'], format11)
        sheet.write(row, col, 'Product Code', format21)
        sheet.write(row, col + 1, 'Product name', format21)
        sheet.write(row, col + 2, 'Quantity', format21)
        sheet.write(row, col + 3, 'UoM', format21)
        sheet.write(row, col + 4, 'Category', format21)
        sheet.write(row, col + 5, 'Avg. Weight', format21)
        sheet.write(row, col + 6, 'Total Weight', format21)


        for product in data['transfer_list']:
            row+=1
            sheet.write(row, col, product['code'], font_size_8)
            sheet.write(row, col + 1, product['product_name'], font_size_8)
            sheet.write(row, col + 2, product['quantity'], font_size_8)
            sheet.write(row, col + 3, product['uom'], font_size_8)
            sheet.write(row, col + 4, product['product_category'], font_size_8)
            sheet.write(row, col + 5, product['avg_weight'], font_size_8)
            sheet.write(row, col + 6, product['total_weight'], font_size_8)






