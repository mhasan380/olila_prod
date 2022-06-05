from odoo import api, fields, models, _
from datetime import datetime, date, timedelta
from odoo.exceptions import UserError
from odoo.tools import float_repr
import datetime, calendar
from calendar import monthrange
from dateutil.relativedelta import relativedelta

class MonthlyRepairingDetailsReportReport(models.AbstractModel):
    _inherit = 'report.olila_transport_reports.monthly_repairing_template'

    def _get_header(self, no_of_month):
        from datetime import datetime, timedelta
        from collections import OrderedDict
        start = date.today() + relativedelta(months=-no_of_month)
        end = date.today()
        total_months = lambda dt: dt.month + 12 * dt.year
        mlist = []
        for tot_m in range(total_months(start)-1, total_months(end)):
            y, m = divmod(tot_m, 12)
            if m == 0:
                head = 'January '+ str(y)
            elif m == 1:
                head = 'February '+str(y)
            elif m == 2:
                head = 'March '+str(y)
            elif m == 3:
                head = 'April '+str(y)
            elif m == 4:
                head = 'May '+str(y)
            elif m == 5:
                head = 'June '+str(y)
            elif m == 6:
                head = 'July '+str(y)
            elif m == 7:
                head = 'August '+str(y)
            elif m == 8:
                head = 'September '+str(y)
            elif m == 9:
                head = 'October '+str(y)
            elif m == 10:
                head = 'November '+str(y)
            elif m == 11:
                head = 'December '+str(y)
            mlist.append(head)
        return mlist

    def _prepare_monthly_repairing_comparison_lines(self, vehicle_ids, date_list, header):
        from datetime import datetime, timedelta
        fleet_services_ids = self.env['fleet.vehicle.log.services'].search([('vehicle_id', 'in', vehicle_ids.ids)])
        lines = []
        header = header
        vehicle_ids = fleet_services_ids.mapped('vehicle_id')
        footer_total = {}
        for head in header:
            footer_total[head] = 0
        total_cost = 0.0
        for vehicle_id in vehicle_ids:
            warehouse = vehicle_id.warehouse_id
            line = {'warehouse': warehouse.name, 'vehicle': vehicle_id and vehicle_id.display_name or '', 'total_repairing_cost': 0}
            month_no = 0
            wm_total = 0
            for month, dates in date_list.items():
                date_start = datetime.strptime(dates['date_from'] + ' 00:00:00', "%Y-%m-%d %H:%M:%S")
                date_end = datetime.strptime(dates['date_to'] + ' 23:59:59', "%Y-%m-%d %H:%M:%S")
                fleet_services = fleet_services_ids.filtered(lambda x: x.vehicle_id.id == vehicle_id.id and x.date >= date_start.date() and x.date <= date_end.date())
                m_total = sum(fleet_services.mapped('amount'))
                line[header[month_no]] =m_total
                wm_total += m_total
                month_key = header[month_no]
                footer_total[month_key] = footer_total[month_key] + m_total
                month_no += 1
            line['total_repairing_cost'] = wm_total
            total_cost += wm_total
            lines.append(line)
        footer_total['total_cost'] = total_cost
        return lines, footer_total



