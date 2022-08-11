from datetime import datetime
from odoo import models, fields, api
import logging
import hashlib
import os

_logger = logging.getLogger(__name__)


class EmployeeLoggerSalesForce(models.Model):
    _name = 'employee.logger.salesforce'

    trace_ip_address = fields.Char(string='Traced IP')
    trace_agent = fields.Char(string='Traced Agent')
    trace_latlng = fields.Char(string='Traced Latitude Longitude')
    trace_location = fields.Char(string='Traced Location')
    employee_id = fields.Many2one('hr.employee', string='Employee')
    log_datetime = fields.Datetime(string='Log Datetime', default=fields.Datetime.now)
    access_credential = fields.Char(string='credential', exportable=False)
    operation = fields.Char(string='operation')
    system_returns = fields.Char(string='system_returns')
    trace_ref = fields.Char(string='trace_ref')
    name = fields.Char(string='Log Name')
    access_type = fields.Selection([('public', 'Public'), ('protected', 'Protected')], string='Access Type')
