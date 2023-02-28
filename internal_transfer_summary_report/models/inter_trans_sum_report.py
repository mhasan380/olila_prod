from odoo import models, fields, api
from datetime import datetime


class InterTransferSumReport(models.AbstractModel):
    _name = 'report.internal_transfer_summary_report.trans_sum_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        product_id = data['form']['product_id']
        product_category = data['form']['product_category']
        category = data['form']['category']
        department_id = data['form']['department_id']
        warehouse_id = data['form']['warehouse_id']
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        location_id = data['form']['location_id']
        transfer_list = {}
        domain = [('picking_id.scheduled_date', '>=', from_date), ('picking_id.scheduled_date', '<=', to_date),
                  ('picking_id.location_id', '=', location_id)]
        if department_id:
            domain.append(('picking_id.department_id', '=', department_id))
        if product_id:
            domain.append(('product_id', '=', product_id))
        if product_category:
            domain.append(('product_id.categ_id', '=', product_category))
        move_lines = self.env['stock.move'].search(domain)

        for line in move_lines:
            key = line.product_id
            transfer_list.setdefault(key, 0.0)
            transfer_list[key] += line.quantity_done

        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'from_date': from_date,
            'to_date': to_date,
            'product_id': product_id,
            'product_category': product_category,
            'category': category,
            'department_id': department_id,
            'warehouse_id': warehouse_id,
            'transfer_list': sorted([{
                'product_id': product.id,
                'product_name': product.name,
                'code': product.default_code,
                'quantity': qty,
                'uom': product.uom_id.name,
                'product_category': product.categ_id.name,
                'avg_weight': product.weight,
                'total_weight': qty * product.weight
            } for (product), qty in transfer_list.items()], key=lambda l: l['code']),
        }
