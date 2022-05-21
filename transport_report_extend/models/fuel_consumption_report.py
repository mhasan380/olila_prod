# -*- coding: utf-8 -*-

from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_repr
import datetime, calendar
from calendar import monthrange
from dateutil.relativedelta import relativedelta

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
                'total' : (line.fuel_purchase * fuel_unit_price),
                'distance' : line.fuel_log_id.total_km
            })
            sr_no+=1
        return lines

# class MonthlyFuelConsumptionReport(models.AbstractModel):
#     _inherit = 'report.olila_transport_reports.monthly_fuel_template'
#
#     def _prepare_monthly_fuel_consumption_lines(self, vehicle_ids, date_list, header):
#         from datetime import datetime, timedelta
#         log_fuel_ids = self.env['fleet.vehicle.log.fuel'].search([('vehicle_id', 'in', vehicle_ids.ids)])
#         lines = []
#         header = header
#         vehicle_ids = log_fuel_ids.mapped('vehicle_id')
#         footer_total = {}
#         for head in header:
#             footer_total[head] = 0
#         total_fuel_cost = 0.0
#         for vehicle_id in vehicle_ids:
#             warehouse = vehicle_id.warehouse_id
#             line = {'warehouse': warehouse.name, 'vehicle': vehicle_id and vehicle_id.display_name or '', 'Total Fuel Cost': 0}
#             month_no = 0
#             wm_total = 0
#             for month, dates in date_list.items():
#                 date_start = datetime.strptime(dates['date_from'] + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
#                 date_end = datetime.strptime(dates['date_to'] + ' 23:59:59', "%Y-%m-%d %H:%M:%S")
#                 log_fuel_filterd_ids = log_fuel_ids.filtered(lambda x: x.vehicle_id.id == vehicle_id.id and x.date >= date_start.date() and x.date <= date_end.date())
#                 m_total = self._get_fuel_log_cost(log_fuel_filterd_ids)
#                 line[header[month_no]] = float_repr(m_total, precision_digits=2)
#                 wm_total += m_total
#                 month_key = header[month_no]
#                 footer_total[month_key] = footer_total[month_key] + m_total
#                 month_no += 1
#             line['total_fuel_cost'] = wm_total
#             total_fuel_cost += wm_total
#             lines.append(line)
#         footer_total['total_fuel_cost'] = total_fuel_cost
#         return lines, footer_total

class VehiclePaperUpdateStatusReport(models.AbstractModel):
    _name = 'report.olila_transport_reports.vehicle_paper_update'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        date = data.get('date')
        vehicle_id = self.env['fleet.vehicle'].browse(data.get('vehicle_id'))
        cost_subtype_id = data.get('cost_subtype_id')

        domain = [('create_date', '<=', date)]
        if vehicle_id:
            domain.append(('vehicle_id', '=', vehicle_id.id))
        if cost_subtype_id:
            domain.append(('cost_subtype_id', '=', cost_subtype_id))

        log_ids = self.env['fleet.vehicle.log.contract'].search(domain)
        lines = []
        for rec in log_ids:
            lines.append({
                'vehicle_id': rec.vehicle_id.name,
                'renew_date': rec.start_date and rec.start_date.strftime('%d-%m-%Y') or '',
                'expire_date': rec.expiration_date and rec.expiration_date.strftime('%d-%m-%Y') or '',
                'document_name': rec.cost_subtype_id.name,
                'state': rec.state,
                'vendor' : rec.insurer_id.name
            })
        return {
            'docs': docs,
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'lines': lines,
        }

