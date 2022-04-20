from odoo import api, fields, models

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    average_weight = fields.Float('Average Weight')
    total_weight = fields.Float('Total Weight')
    shift = fields.Selection([('a', 'A Shift'), ('b', 'B Shift'), ('c', 'C Shift')],string='Shift')
    production_type = fields.Selection([('pcs', 'PCS'), ('ei', 'Empty Inner'), ('emm', 'Empty Master'),('fgi', 'FG Inner'),
                ('fgm', 'FG Master'), ('cullet', 'Cullet'), ('converstion', 'Conversion')],string='Production Type')

    @api.onchange('average_weight','product_qty')
    def onchange_average_weight(self):
        for mo in self:
            if mo.average_weight:
                mo.total_weight = mo.average_weight * mo.product_qty

