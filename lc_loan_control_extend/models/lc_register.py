# -*- coding: utf-8 -*-


from odoo import models, fields, api

class LcRegister(models.Model):
    _inherit = 'lc.register'

    lc_no = fields.Char('LC Number')