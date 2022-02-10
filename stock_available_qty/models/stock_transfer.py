
from odoo import api, fields, models, _
from odoo.exceptions import UserError

class StockTransferLine(models.Model):
    _inherit = 'stock.transfer.line'

    available_qty = fields.Float(string='Available qty',compute="_compute_available_qty")

    @api.depends('transfer_id.location_id','product_id')
    def _compute_available_qty(self):
        for line in self:
            stock = self.env['stock.quant'].search([('location_id', '=', line.transfer_id.location_id.id),('product_id', '=', line.product_id.id)])
            total_qty = 0.0
            for item in stock:
                total_qty = total_qty + item.quantity
            line.available_qty = total_qty










    

                
