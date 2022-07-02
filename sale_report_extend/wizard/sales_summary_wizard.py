from odoo import models, fields, api
from odoo.tools import date_utils
from datetime import datetime, timedelta


class SalesSummaryWizard(models.TransientModel):
    _name = "sales.summary.wizard"
    _description = "Sales Summary Report Wizard"

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    zone_id = fields.Many2one('res.zone', string="Zone")

    def get_report(self):
        zone_id = self.zone_id

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'zone_id': zone_id.name,
                'from_date': self.from_date,
                'to_date': self.to_date
            },
        }

        return self.env.ref('sale_report_extend.sales_summary_report').report_action(self, data=data)


class SalesSummaryReport(models.AbstractModel):
    _name = 'report.sale_report_extend.sales_summary_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        zone_id = data['form']['zone_id']
        date_start = data['form']['from_date']
        date_end = data['form']['to_date']

        from_date = datetime.combine(datetime.strptime(date_start, "%Y-%m-%d"), datetime.min.time())
        to_date = datetime.combine(datetime.strptime(date_end, "%Y-%m-%d"), datetime.max.time())

        sale_orders = self.env['sale.order'].search([('date_order', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")),
                                                     ('date_order', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S"))])
        if zone_id:
            sale_orders = self.env['sale.order'].search(
                [('zone_id', '=', zone_id),
                 ('date_order', '>=', from_date.strftime("%Y-%m-%d %H:%M:%S")), ('date_order', '<=', to_date.strftime("%Y-%m-%d %H:%M:%S"))])
            zones = self.env['res.zone'].search([('name', '=', zone_id)])
        else:
            zones = self.env['res.zone'].search([])

        lines = []
        for zone in zones:
            orders = []
            pcs_qty = 0
            inner_qty = 0
            master_qty = 0
            total_value = 0.0
            for order in sale_orders:
                if order.zone_id == zone:
                    orders.append(order)
            for record in orders:
                for line in record.order_line:
                    if line.product_id.fs_type == 'pcs':
                        pcs_qty += line.product_uom_qty
                    elif line.product_id.fs_type == 'inner':
                        inner_qty += line.product_uom_qty
                    elif line.product_id.fs_type == 'master':
                        master_qty += line.product_uom_qty
                total_value += record.amount_total

            lines.append({'zone': zone.name,
                          'pcs_qty': pcs_qty,
                          'inner_qty': inner_qty,
                          'master_qty': master_qty,
                          'total_value': total_value
                          })

        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'sale_orders': sale_orders,
            'zone_id': zone_id,
            'from_date': from_date,
            'to_date': to_date,
            'lines': lines
        }
