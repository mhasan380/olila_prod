from odoo import api, fields, models, _

class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    is_3rd_party = fields.Boolean('3rd Party')
    responsible = fields.Many2one('res.partner',string="Responsible")