# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class FuelConsumptionReport(models.AbstractModel):
    _inherit = 'report.olila_transport_reports.fuel_consumption_template'

    def _prepare_fuel_consumption_lines(self, vehicle_ids, date_from, date_to, fuel_type):
        domain = [('fuel_log_id.vehicle_id', 'in', vehicle_ids.ids), ('fuel_log_id.date', '>=', date_from), ('fuel_log_id.date', '<=', date_to)]
        if fuel_type:
            domain.append(('fuel_type', '=', fuel_type))
        log_fuel_ids = self.env['fuel.purchase.history'].search(domain)
        fuel_types = {'gasoline': 'Petrol', 'lpg': 'CNG', 'diesel': 'Diesel' , 'octane': 'Octane'}
        lines = []
        sr_no = 1
        warehouse_ids = log_fuel_ids.mapped('fuel_log_id.vehicle_id').mapped('warehouse_id')
        for line in log_fuel_ids.filtered(lambda x: x.fuel_log_id.vehicle_id.warehouse_id.id in warehouse_ids.ids):
            fuel_unit_price = line.amount / line.fuel_purchase if line.fuel_purchase and line.amount else 0.0
            lines.append({
                'sr_no': sr_no,
                'date': line.purchase_date and line.purchase_date.strftime('%d-%m-%Y') or '',
                'vehicle': line.fuel_log_id.vehicle_id.display_name if line.fuel_log_id.vehicle_id else '',
                'depot': line.fuel_log_id.vehicle_id.warehouse_id.name if line.fuel_log_id.vehicle_id and line.fuel_log_id.vehicle_id.warehouse_id else '',
                'fuel_type': fuel_types.get(line.fuel_type, ''),
                'fuel_qty' : line.fuel_purchase,
                'fuel_unit_price' : round(fuel_unit_price, 2),
                'total' : round((line.fuel_purchase * fuel_unit_price), 2),
                'distance' : line.total_km
            })
            sr_no+=1
        return lines