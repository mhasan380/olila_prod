from odoo import models, fields, api


class VehiclePaperCostWizard(models.TransientModel):
    _name = "vehicle.paper.cost.wizard"
    _description = "Print Vehicle Paper Cost Report Wizard"

    vehicle_id = fields.Many2one('fleet.vehicle', string="Vehicle")
    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    doc_type = fields.Many2one('fleet.service.type', domain="[('category', '=', 'contract')]", string='Document Type')

    def get_report(self):
        vehicle_id = self.vehicle_id
        doc_type = self.doc_type

        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'vehicle_id': vehicle_id.name,
                'doc_type': doc_type.name,
                'from_date': self.from_date,
                'to_date': self.to_date
            },
        }
        return self.env.ref('transport_reports_olila.vehicle_doc_cost_report').report_action(self, data=data)


class VehiclePaperCostReport(models.AbstractModel):
    _name = 'report.transport_reports_olila.vehicle_doc_cost_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        vehicle_id = data['form']['vehicle_id']
        doc_type = data['form']['doc_type']
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']

        documents = self.env['vehicle.liecense.renew'].search([('date_from', '>=', from_date),
                                                               ('date_from', '<=', to_date)])
        if vehicle_id:
            documents = self.env['vehicle.liecense.renew'].search(
                [('licence_id.vehicle_id', '=', vehicle_id),
                 ('date_to', '>=', from_date), ('date_to', '<=', to_date)])
        if doc_type:
            documents = self.env['vehicle.liecense.renew'].search(
                [('licence_id', 'ilike', doc_type),
                 ('date_to', '>=', from_date), ('date_to', '<=', to_date)])
        if vehicle_id and doc_type:
            documents = self.env['vehicle.liecense.renew'].search(
                [('licence_id.vehicle_id', '=', vehicle_id), ('licence_id', 'ilike', doc_type),
                 ('expiration_date', '>=', from_date), ('expiration_date', '<=', to_date)])

        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'documents': documents,
            'vehicle_id': vehicle_id,
            'doc_type': doc_type,
            'from_date': from_date,
            'to_date': to_date,

        }
