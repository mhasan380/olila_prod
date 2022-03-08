# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models

class SaleReport(models.Model):
    _inherit = "sale.report"

    responsible = fields.Many2one('hr.employee', string="Responsible", readonly=True)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['responsible'] = ", s.responsible as responsible"
        groupby += ', s.responsible'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

