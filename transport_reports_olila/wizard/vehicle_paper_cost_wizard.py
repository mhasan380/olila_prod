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
        return self.env.ref('transport_reports_olila.vehiclewise_doc_cost_report').report_action(self, data=data)
