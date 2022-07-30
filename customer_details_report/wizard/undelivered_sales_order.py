from datetime import datetime
from odoo import models, fields, api


class UndeliveredSalesOrderWizard(models.TransientModel):
    _name = 'undelivered.so.wizard'
    _description = "Undelivered Sales Order Report Wizard"

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    date = fields.Date('Date')
    partner_id = fields.Many2one('res.partner', string='Customer')
    sale_type = fields.Selection([('primary_sales', 'Primary Sales'), ('corporate_sales', 'Corporate Sales')],
                                 default='primary_sales')

    def get_report(self):
        partner_id = self.partner_id
        sale_type = self.sale_type

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'from_date': self.from_date,
                'to_date': self.to_date,
                'partner_id': partner_id.name,
                'sale_type': sale_type
            },
        }

        return self.env.ref('customer_details_report.undelivered_so_report').report_action(self, data=data)


class UndeliveredSalesOrderReport(models.AbstractModel):
    _name = 'report.customer_details_report.undelivered_so_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        partner_id = data['form']['partner_id']
        sale_type = data['form']['sale_type']

        undelivered_dict = {}
        product_dict = {}

        if partner_id:
            sale_orders = self.env['sale.order'].search(
                [('partner_id', '=', partner_id), ('date_order', '>=', from_date),
                 ('date_order', '<=', to_date)])

        elif sale_type:
            sale_orders = self.env['sale.order'].search(
                [('sale_type', '=', sale_type), ('date_order', '>=', from_date), ('date_order', '<=', to_date)])

        else:
            sale_orders = self.env['sale.order'].search(
                [('date_order', '>=', from_date), ('date_order', '<=', to_date)])

        for sale in sale_orders:
            do = self.env['stock.picking'].search(
                [('origin', '=', sale.name), ('state', 'in', ('confirmed', 'assigned'))])
            for order in do:
                for line in order.move_ids_without_package:
                    key = line.product_id
                    product_dict.setdefault(key, 0.0)
                    product_dict[key] += line.product_uom_qty

            if product_dict:
                row = True
            else:
                row = False
            undelivered_dict.update({sale.name: {'sale_code': sale.name, 'date_order': sale.date_order,
                                                 'customer_code': sale.partner_id.code,
                                                 'customer_name': sale.partner_id.name,
                                                 'depot': sale.warehouse_id.name,
                                                 'product_dict': product_dict,
                                                 'row': row
                                                 }})

            product_dict = dict.fromkeys(product_dict, 0)

        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'sale_type': sale_type,
            'partner_id': partner_id,
            'from_date': from_date,
            'to_date': to_date,
            'undelivered_dict': list(undelivered_dict.values())
        }
