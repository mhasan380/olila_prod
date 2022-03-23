# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
	_inherit = "account.move"

	lc_ammend_id = fields.Many2one("purchase.lc.ammendment", string='LC Ammend')