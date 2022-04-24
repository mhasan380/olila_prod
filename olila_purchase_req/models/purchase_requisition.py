#-*- coding: utf-8 -*-

from datetime import datetime, time
from odoo import models, fields, api

class PurchaseRequisition(models.Model):
    _inherit = "purchase.requisition"

    ref_number = fields.Char("Product Code")

    def select_product(self):
        for line in self.line_ids:
            if line.product_id.default_code == self.ref_number:
                line.to_purchase = True
        self.ref_number = ""

    def create_po(self):
        context = self._context
        current_uid = context.get('uid')
        user = self.env['res.users'].browse(current_uid)
        vals = { 'partner_id' : self.vendor_id.id,
                 'requisition_id' : self.id,
                 'currency_id' : self.currency_id.id,
                  'date_order' : fields.Datetime.today(),
                  'date_planned' : fields.Datetime.today(),
                  'origin' : self.origin,
                  'department_id' : self.department_id.id,
                  'user_id' : user.id,
                  'purchase_type': self.vendor_id.olila_seller_type

          }

        purchase_order = self.env['purchase.order'].create(vals)

        filb_values = []
        for line in self.line_ids:
            if line.to_purchase == True:

                prod = (0, 0, {

                            'product_id': line.product_id.id,
                            'product_uom': line.product_id.uom_po_id.id,
                            'product_qty': line.product_qty,
                            'price_unit': 1.0,
                             'warehouse_id': user.property_warehouse_id.id,
                            'date_planned': datetime.now(),
                            'account_analytic_id': line.account_analytic_id.id,
                            'analytic_tag_ids': line.analytic_tag_ids.ids,
                             })
                filb_values.append(prod)
                line.to_purchase = False
        purchase_order.update({
                'order_line': filb_values,
            })




class PurchaseRequisitionLine(models.Model):
    _inherit = "purchase.requisition.line"

    to_purchase = fields.Boolean()






