# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
	_inherit = "account.move"

	lc_fund_req_id = fields.Many2one("lc.opening.fund.requisition", string='LC Fund Req')