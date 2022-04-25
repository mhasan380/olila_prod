from odoo import api, fields, models

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    requisition_month = fields.Date('Requisition Month')


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    department = fields.Many2one('hr.department', string='Department')

    @api.onchange('product_id')
    def onchange_product(self):
        if self.product_id:
            self.available_qty = self.product_id.qty_available
