from datetime import datetime
from odoo import models, fields
import logging

_logger = logging.getLogger(__name__)

""" ===========Code Statements========
 **public_token - used to verify client
 
 **access_code
 
"""


class AppConfig(models.Model):
    _name = 'app.config'

    public_token = fields.Char(string='public_token', groups='base.group_system', copy=False)
    version_down = fields.Char(string='version_down')
    version_up = fields.Char(string='version_up')
    version_code = fields.Integer(string='version_code')
    custom_message = fields.Char(string='custom_message')
    is_under_maintenance = fields.Boolean(default=False, invisible=True)

