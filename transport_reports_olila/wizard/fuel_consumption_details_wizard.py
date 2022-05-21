from odoo import models, fields, api


class FuelConsumptionDetailsWizard(models.TransientModel):
    _name = "fuel.consumption.details.wizard"
    _description = "Print Vehicle Fuel Consumption Details Report Wizard"

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    fuel_type = fields.Many2one('fuel.fuel', string="Fuel Type")
    depot_id = fields.Many2one('stock.warehouse', string="Depot Name")

    def get_report(self):
        vehicle_id = self.vehicle_id
        fuel_type = self.fuel_type
        depot_id = self.depot_id

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'vehicle_id': vehicle_id.name,
                'fuel_type': fuel_type.name,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'depot_id': depot_id.name
            },
        }
        return self.env.ref('transport_reports_olila.fuel_consumption_report').report_action(self, data=data)


class FuelConsumptionDetailsReport(models.AbstractModel):
    _name = 'report.transport_reports_olila.fuel_consumption_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        vehicle_id = data['form']['vehicle_id']
        fuel_type = data['form']['fuel_type']
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']

        documents = self.env['fleet.vehicle.log.fuel'].search([('date', '>=', from_date),
                                                               ('date', '<=', to_date)])
        if vehicle_id:
            documents = self.env['fleet.vehicle.log.contract'].search(
                [('vehicle_id', '=', vehicle_id),
                 ('expiration_date', '>=', from_date), ('expiration_date', '<=', to_date)])
        if doc_type:
            documents = self.env['fleet.vehicle.log.contract'].search(
                [('cost_subtype_id', '=', doc_type),
                 ('expiration_date', '>=', from_date), ('expiration_date', '<=', to_date)])
        if vehicle_id and doc_type:
            documents = self.env['fleet.vehicle.log.contract'].search(
                [('vehicle_id', '=', vehicle_id), ('cost_subtype_id', '=', doc_type),
                 ('expiration_date', '>=', from_date), ('expiration_date', '<=', to_date)])

        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'documents': documents,
            'vehicle_id': vehicle_id,
            'doc_type': doc_type,
            'from_date': from_date,
            'to_date': to_date
        }
