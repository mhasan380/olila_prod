from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"

    is_lc = fields.Boolean('IS LC?')
