# -*- coding: utf-8 -*-
from odoo import tools
from odoo import api, fields, models

class SaleReport(models.Model):
    _inherit = "sale.report"

    responsible = fields.Many2one('hr.employee', string="Responsible", readonly=True)
    sale_type = fields.Selection(selection=[('primary_sales', 'Primary Sales'),
                                            ('secondary_sales', 'Secondary Sales'),
                                            ('corporate_sales', 'Corporate Sales')], default="primary_sales",
                                 string="Sale Type")
    zone_id = fields.Many2one('res.zone', string='Zone', copy=False)

    def _query(self, with_clause='', fields={}, groupby='', from_clause=''):
        fields['responsible'] = ", s.responsible as responsible"
        groupby += ', s.responsible'
        fields['sale_type'] = ", s.sale_type as sale_type"
        groupby += ', s.sale_type'
        fields['zone_id'] = ", s.zone_id as zone_id"
        groupby += ', s.zone_id'
        return super(SaleReport, self)._query(with_clause, fields, groupby, from_clause)

