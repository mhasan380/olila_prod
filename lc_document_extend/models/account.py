# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError

class AccountMove(models.Model):
	_inherit = "account.move"

	lc_drl_id = fields.Many2one("document.release.letter", string='LC Document Release')