from odoo import models, fields, api
from datetime import datetime


class InterTransferSumWizard(models.TransientModel):
    _name = 'transfer.summary.wizard'
    _description = 'Daily Internal Transfer Summary productwise'

    product_id = fields.Many2one('product.product', string='Product')
    department_id = fields.Many2one('hr.department', string='Department')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def get_pdf_report(self):
        product_id = self.product_id
        department_id = self.department_id

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'product_id': product_id.name,
                'department_id': department_id.name,
                'warehouse_id': self.warehouse_id.name,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'location_id': self.warehouse_id.lot_stock_id.id
            },
        }
        return self.env.ref('internal_transfer_summary_report.transfer_sum_report').report_action(self, data=data)

    def get_xls_report(self):
        transfer_list ={}
        domain = [('picking_id.scheduled_date', '>=', self.from_date), ('picking_id.scheduled_date', '<=', self.to_date),
                  ('picking_id.location_id', '=', self.warehouse_id.lot_stock_id.id)]
        if self.department_id:
            domain.append(('picking_id.department_id', '=', self.department_id.id))
        if self.product_id:
            domain.append(('product_id', '=', self.product_id.id))
        move_lines = self.env['stock.move'].search(domain)

        for line in move_lines:
            key = (line.product_id)
            transfer_list.setdefault(key, 0.0)
            transfer_list[key] += line.quantity_done

        data = {

            'from_date': self.from_date,
            'to_date': self.to_date,
            'product_id': self.product_id,
            'department_id': self.department_id,
            'warehouse_id': self.warehouse_id,
            'transfer_list': sorted([{
                        'product_id': product.id,
                        'product_name': product.name,
                        'code': product.default_code,
                        'quantity': qty,
                        'uom': product.uom_id.name,
                    } for (product), qty in transfer_list.items()], key=lambda l: l['code']),

        }
        return self.env.ref('internal_transfer_summary_report.transfer_sum_xlsx').report_action(self, data=data)


