# -*- coding: utf-8 -*-

from odoo import api, fields, models

class AttendanceSummaryLine(models.Model):
    _inherit = 'hr.attendance.summary.line'
    emp_id = fields.Char(string='ID', related='employee_id.identification_id')

