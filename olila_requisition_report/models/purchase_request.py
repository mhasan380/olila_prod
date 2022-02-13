from odoo import api, fields, models

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

    requisition_month = fields.Date('Requisition Month')