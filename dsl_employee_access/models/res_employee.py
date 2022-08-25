from datetime import datetime
from odoo import models, fields, api
import logging
import hashlib
import os

_logger = logging.getLogger(__name__)

""" ===========Code Statements========
 **employee_type
 National sales Manager(NSM)-->Regional Sales Manager(RSM)--->
 Zonal Sales Manager(ZSM)--->Area Sales Manager(ASM)--->Sales officer(SO)-->Sales Representative(SR)
 
 **access_code
 
"""


class EmployeeAccess(models.Model):
    _inherit = 'hr.employee'

    is_enable_sales_force = fields.Boolean(string='Enable Sales Force')
    active_status = fields.Boolean(string='Active App Login')
    # app_employee_type = fields.Selection(string="App User Type", selection=[
    #     ('nsm', 'National sales Manager(NSM)'),
    #     ('rsm', 'Regional Sales Manager(RSM)'),
    #     ('zsm', 'Zonal Sales Manager(ZSM)'),
    #     ('asm', 'Area Sales Manager(ASM)'),
    #     ('so', 'Sales officer(SO)'),
    #     ('sr', 'Sales Representative(SR)')
    # ])
    temp_code_crypto = fields.Char(string='temp', store=True, groups='dsl_employee_access.group_hr_employee_access_app_login')
    wrong_temp_code_count = fields.Integer(string='temp_count', copy=False, store=True, groups='dsl_employee_access.group_hr_employee_access_app_login')
    access_code = fields.Char(string='Set Access Code', copy=False, store=False, )
    access_code_crypto = fields.Char(string='crypt', compute='onchange_access_code', store=True,groups='dsl_employee_access.group_hr_employee_access_app_login')
    access_token = fields.Char(string='token_access', copy=False, groups='dsl_employee_access.group_hr_employee_access_app_login')
    wrong_code_data = fields.Char(string='wrong_code_data', groups='dsl_employee_access.group_hr_employee_access_app_login')
    wrong_code_time = fields.Char(string='wrong_code_time', groups='dsl_employee_access.group_hr_employee_access_app_login')
    wrong_code_count = fields.Integer(string='wrong_code_count', copy=False, groups='dsl_employee_access.group_hr_employee_access_app_login')
    is_wrong_code_limit_exceeded = fields.Boolean(default=False, invisible=True)

    is_temp_code_count_limit_exceeded = fields.Boolean(string="temp_count_exceeded", compute='action_temp_code_restriction_check', default=False)

    # def fields_get(self, fields=None):
    #     hide = ['access_code_crypto', 'access_token', 'wrong_code_data', 'wrong_code_time',
    #             'is_wrong_code_limit_exceeded', 'wrong_code_count']
    #     res = super(EmployeeAccess, self).fields_get()
    #     for field in hide:
    #         res[field]['searchable'] = False
    #         res[field]['sortable'] = False
    #         res[field]['exportable'] = False
    #     return res

    @api.depends('access_code')
    def onchange_access_code(self):
        for rec in self:
            if rec.access_code:
                # salt = os.urandom(32)
                # self.access_code_crypto = hashlib.pbkdf2_hmac('sha256', self.access_code.encode('utf8'), salt, 100000)
                rec.access_code_crypto = rec.to_hash(self.access_code)

    def _compute_wrong_code_data(self):

        now = datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()), "%Y-%m-%d %H:%M:%S")
        self.wrong_code_data = f'{now}'
        if not self.wrong_code_time:
            self.wrong_code_time = f'{now}'

    def _compute_is_wrong_code_limit_exceeded(self):
        if not self.wrong_code_data:
            self.is_wrong_code_limit_exceeded = False
        else:
            self.is_wrong_code_limit_exceeded = True

    def to_hash(self, value):
        return str(hashlib.md5(value.encode('utf8')).hexdigest())

    def action_revoke_temp_code_restriction(self):
        self.wrong_temp_code_count = 0

    @api.depends('wrong_temp_code_count')
    def action_temp_code_restriction_check(self):
        if self.wrong_temp_code_count < 5:
            self.is_temp_code_count_limit_exceeded = False
        else:
            self.is_temp_code_count_limit_exceeded = True

    def action_revoke_restriction(self):
        self.wrong_code_time = False
        self.wrong_code_count = 0
        self.is_wrong_code_limit_exceeded = False
        # now = datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()), "%Y-%m-%d %H:%M:%S")
        #
        # if self.wrong_code_time:
        #     that_time = datetime.strptime(self.wrong_code_time, "%Y-%m-%d %H:%M:%S")
        #     current_time = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
        #     fixed_interval = datetime.strptime("2022-05-25 17:00:00", "%Y-%m-%d %H:%M:%S") - datetime.strptime(
        #         "2022-05-25 16:00:00", "%Y-%m-%d %H:%M:%S")
        #     interval = current_time - that_time
        #     _logger.warning(f'time difference1----------> {current_time - that_time}')
        #     _logger.warning(f'time difference2----------> {fixed_interval}')
        #
        #     if fixed_interval > interval:
        #         _logger.warning(f'time int true----------> {fixed_interval}')
        #     else:
        #         _logger.warning(f'time int false----------> {interval}')
        #
        # else:
        #     # now = datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()), "%Y-%m-%d %H:%M:%S")
        #     self.wrong_code_time = f'{now}'
        #     # self.wrong_code_data = f'1 && {now}'

    # now=datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()), "%Y-%m-%d %H:%M:%S")

    # company_id = fields.Many2one('res.company', 'Company', copy=False, readonly=True, help="Company",
    #                              default=lambda self: self.env.user.company_id)
    # auto_order_ids = fields.Many2many('sale.order', 'invoice_sale_orders_rel', 'invoice_id', 'sale_order_id',
    #                                   string='Orders to Auto-Fill',
    #                                   domain="[('partner_id', '=', partner_id) , ('company_id', '=', company_id)]")

    def restrict_action(self, employee_id):
        _logger.warning(f'time data----------> {self.wrong_code_time}')
        _logger.warning(f'model function called----------> {employee_id}')
        now = datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()), "%Y-%m-%d %H:%M:%S")

        if self.wrong_code_time:
            that_time = datetime.strptime(self.wrong_code_time, "%Y-%m-%d %H:%M:%S")
            current_time = datetime.strptime(now, "%Y-%m-%d %H:%M:%S")
            fixed_interval = datetime.strptime("2022-05-25 17:00:00", "%Y-%m-%d %H:%M:%S") - datetime.strptime(
                "2022-05-25 16:00:00", "%Y-%m-%d %H:%M:%S")
            interval = current_time - that_time
            # _logger.warning(f'time difference1----------> {current_time - that_time}')
            # _logger.warning(f'time difference2----------> {fixed_interval}')

            if fixed_interval > interval:
                _logger.warning(f'time int true----------> {fixed_interval}')
            else:
                _logger.warning(f'time int false----------> {interval}')

        else:
            _logger.warning(f'model function called2----------> {employee_id}')
            # now = datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()), "%Y-%m-%d %H:%M:%S")
            self.wrong_code_time = f'{now}'
            # self.wrong_code_data = f'1 && {now}'

    def get_date_time_now(self):
        return datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()), "%Y-%m-%d %H:%M:%S")
