# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
	_inherit = "account.move"

	lc_insurence_id = fields.Many2one("insurance.cover", string='LC Insurence')