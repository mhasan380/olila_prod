from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    average_weight = fields.Float('Average Weight')
    total_weight = fields.Float('Total Weight')
    shift = fields.Selection([('a', 'A Shift'), ('b', 'B Shift'), ('c', 'C Shift')],string='Shift')

    @api.onchange('average_weight')
    def onchange_average_weight(self):
        for mo in self:
            if mo.average_weight:
                mo.total_weight = mo.average_weight * mo.product_qty

