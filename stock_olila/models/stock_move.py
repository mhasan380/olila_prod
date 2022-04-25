from odoo import fields, models, api

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    available_qty = fields.Float(string='Available qty', compute="_compute_available_qty")

    @api.depends('location_id', 'product_id')
    def _compute_available_qty(self):
        for line in self:
            stock = self.env['stock.quant'].search(
                [('location_id', '=', line.location_id.id), ('product_id', '=', line.product_id.id)])
            total_qty = 0.0
            for item in stock:
                total_qty = total_qty + item.quantity
            line.available_qty = total_qty