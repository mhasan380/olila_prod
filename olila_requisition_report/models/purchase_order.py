from odoo import fields, models

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    def change_po_state(self):
        self.state = 'cancel'




