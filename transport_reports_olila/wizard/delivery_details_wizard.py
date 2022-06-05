from odoo import models, fields, api


class DeliveryDetailsWizard(models.TransientModel):
    _name = "delivery.details.wizard"
    _description = "Print Delivery Details Report Wizard"

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    depot_id = fields.Many2one('stock.warehouse', string="Depot")

    def get_report(self):
        vehicle_id = self.vehicle_id
        depot_id = self.depot_id

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'vehicle_id': vehicle_id.name,
                'depot_name': depot_id.name,
                'from_date': self.from_date,
                'to_date': self.to_date
            },
        }
        return self.env.ref('transport_reports_olila.delivery_details_report').report_action(self, data=data)


class DeliveryDetailsReport(models.AbstractModel):
    _name = 'report.transport_reports_olila.delivery_details_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        vehicle_id = data['form']['vehicle_id']
        depot_id = data['form']['depot_id']
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']

        distributions = self.env['vehicle.distribution'].search([('date', '>=', from_date),
                                                             ('date', '<=', to_date)])
        if vehicle_id:
            distributions = self.env['vehicle.distribution'].search(
                [('vehicle_id', '=', vehicle_id),
                 ('date', '>=', from_date), ('date', '<=', to_date)])
        if depot_id:
            distributions = self.env['vehicle.distribution'].search(
                [('', '=', depot_id),
                 ('date', '>=', from_date), ('date', '<=', to_date)])
        if vehicle_id and depot_id:
            distributions = self.env['vehicle.distribution'].search(
                [('vehicle_id', '=', vehicle_id), ('', '=', depot_id),
                 ('date', '>=', from_date), ('date', '<=', to_date)])
        for distribution in distributions:
            product_qty = 0
            for line in distribution.product_line_ids:
                product_qty = line.product_qty + product_qty


        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'distributions': distributions,
            'vehicle_id': vehicle_id,
            'depot_id': depot_id,
            'from_date': from_date,
            'to_date': to_date
        }
