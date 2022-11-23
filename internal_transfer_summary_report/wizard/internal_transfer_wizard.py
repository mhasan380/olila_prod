from odoo import models, fields, api
from datetime import datetime


class InternalTransferWizard(models.TransientModel):
    _name = 'internal.transfer.wizard'
    _description = 'Daily Internal Transfer Summary SR Wise'

    product_id = fields.Many2one('product.product', string='Product')
    department_id = fields.Many2one('hr.department', string='Department')
    warehouse_id = fields.Many2one('stock.warehouse', string='Warehouse')
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")

    def get_report(self):
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
        return self.env.ref('internal_transfer_summary_report.internal_transfer_report').report_action(self, data=data)


class InternalTransferReport(models.AbstractModel):
    _name = 'report.internal_transfer_summary_report.int_trans_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        product_id = data['form']['product_id']
        department_id = data['form']['department_id']
        warehouse_id = data['form']['warehouse_id']
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        location_id = data['form']['location_id']
        transfer_list = []
        documents = self.env['stock.picking'].search([('scheduled_date', '>=', from_date),
                                                      ('scheduled_date', '<=', to_date),
                                                      ('location_id', '=', location_id)])

        if department_id and not product_id:
            documents = self.env['stock.picking'].search([('scheduled_date', '>=', from_date),
                                                          ('scheduled_date', '<=', to_date),
                                                          ('location_id', '=', location_id),
                                                          ('department_id', '=', department_id)])

            for transfer in documents:
                for line in transfer.move_ids_without_package:
                    if line.product_uom_qty != 0:
                        transfer_list.append([transfer.scheduled_date, transfer.name,
                                              transfer.location_id.location_id.name,
                                              transfer.location_dest_id.name, transfer.department_id.name,
                                              line.product_id.default_code, line.product_id.name, line.quantity_done,
                                              line.product_uom.name, transfer.note, transfer.user_id.name,
                                              transfer.state])
        elif product_id and department_id:
            documents = self.env['stock.picking'].search([('scheduled_date', '>=', from_date),
                                                          ('scheduled_date', '<=', to_date),
                                                          ('location_id', '=', location_id),
                                                          ('department_id', '=', department_id)])

            for transfer in documents:
                for line in transfer.move_ids_without_package:
                    if line.product_id.name == product_id:
                        transfer_list.append([transfer.scheduled_date, transfer.name,
                                              transfer.location_id.location_id.name,
                                              transfer.location_dest_id.name, transfer.department_id.name,
                                              line.product_id.default_code, line.product_id.name, line.quantity_done,
                                              line.product_uom.name, transfer.note, transfer.user_id.name,
                                              transfer.state])
                        print(transfer_list)

        elif product_id and not department_id:
            documents = self.env['stock.picking'].search([('scheduled_date', '>=', from_date),
                                                          ('scheduled_date', '<=', to_date),
                                                          ('location_id', '=', location_id)])
            for transfer in documents:
                for line in transfer.move_ids_without_package:
                    if line.product_id.name == product_id:
                        transfer_list.append([transfer.scheduled_date, transfer.name,
                                              transfer.location_id.location_id.name,
                                              transfer.location_dest_id.name, transfer.department_id.name,
                                              line.product_id.default_code, line.product_id.name,
                                              line.quantity_done,
                                              line.product_uom.name, transfer.note, transfer.user_id.name,
                                              transfer.state])
        else:
            for transfer in documents:
                for line in transfer.move_ids_without_package:
                    if line.product_uom_qty != 0:
                        transfer_list.append([transfer.scheduled_date, transfer.name,
                                              transfer.location_id.display_name,
                                              transfer.location_dest_id.display_name, transfer.department_id.name,
                                              line.product_id.default_code, line.product_id.name, line.quantity_done,
                                              line.product_uom.name, transfer.note, transfer.user_id.name,
                                              transfer.state])
        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'from_date': from_date,
            'to_date': to_date,
            'product_id': product_id,
            'department_id': department_id,
            'warehouse_id': warehouse_id,
            'transfer_list': transfer_list
        }
