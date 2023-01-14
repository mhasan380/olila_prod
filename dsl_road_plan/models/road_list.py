# -*- coding: utf-8 -*-
import werkzeug
import requests
from datetime import datetime
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT, float_compare, translate


# UNIT = dp.get_precision("Location")
#
#
# def urlplus(url, params):
#     return werkzeug.Href(url)(params or None)


class CheckList(models.Model):
    _name = 'rode.list'
    name = fields.Char('Name')
    name_work = fields.Text('Task')
    route_id = fields.Many2one('sales.person.plan', string="Route ID")
    track_status = fields.Char('Track Stage Change', store=True, compute='_onchange_status')
    remarks = fields.Text('Remarks')
    customer = fields.Many2one('res.partner', string='Customer')
    street = fields.Char(related='customer.street', string='Street')
    status = fields.Selection(string="Status", selection=[('todo', 'To Do'), ('done', 'Done'),
                                                          ('progress', 'In Progress'), ('incomplete', 'Incomplete'),
                                                          ('cancel', 'Cancel')], readonly=True,default='todo')
    # secondary_customer = fields.Many2one('customer.secondary', string="Secondary Customer")
    incomplete_reason = fields.Selection(string="Incomplete Reason", selection=[('reason1', 'Shop owner was not there'),
                                                                                ('reason2', 'Shop was closed'),
                                                                                ('reason3', 'Not enough money'),
                                                                                ('reason4', 'Enough stock available in shop'),
                                                                                ('others', 'Others')], readonly=True)

    start_time = fields.Datetime(string="Start")
    end_time = fields.Datetime(string="End")
    duration_time = fields.Char(string="Duration")


    check_in_latitude = fields.Char(
        "Check-in Latitude",
        readonly=True
    )
    check_in_longitude = fields.Char(
        "Check-in Longitude",
        readonly=True
    )
    check_out_latitude = fields.Char(
        "Check-out Latitude",
        readonly=True
    )
    check_out_longitude = fields.Char(
        "Check-out Longitude",
        readonly=True
    )
    check_in_map_link = fields.Char('Check In Map',
                                    compute='_compute_check_in_map_url'
                                    )
    check_out_map_link = fields.Char('Check Out Map',
                                     compute='_compute_check_out_map_url'
                                     )

    @api.depends('status')
    def _onchange_status(self):
        now_time = datetime.strftime(fields.Datetime.context_timestamp(self, datetime.now()), "%Y-%m-%d %H:%M:%S")
        for rec in self:
            if rec.track_status:
                rec.track_status = f'{rec.track_status} -> {rec.status} : {now_time}'
            else:
                rec.track_status = f'todo : {now_time}'
            if rec.status == 'progress':
                rec.start_time = now_time
            if rec.status == 'done':
                rec.end_time = now_time
                if rec.start_time:
                    rec.duration_time = str(rec.end_time-rec.start_time)

    @api.depends('check_in_latitude', 'check_in_longitude')
    def _compute_check_in_map_url(self):
        for record in self:
            link_builder = f'https://www.google.com/maps/place/{record.check_in_latitude}+{record.check_in_longitude}/@{record.check_in_latitude},{record.check_in_longitude},17z'
            if record.check_in_latitude and record.check_in_longitude:
                record.check_in_map_link = link_builder
            else:
                record.check_in_map_link = ''

    @api.depends('check_out_latitude', 'check_out_longitude')
    def _compute_check_out_map_url(self):
        for record in self:
            link_builder = f'https://www.google.com/maps/place/{record.check_out_latitude}+{record.check_out_longitude}/@{record.check_out_latitude},{record.check_out_longitude},17z'
            if record.check_out_latitude and record.check_out_longitude:
                record.check_out_map_link = link_builder
            else:
                record.check_out_map_link = ''

    def do_accept(self):

        self.write({
            'status': 'done',
        })

    def do_cancel(self):
        self.write({
            'status': 'cancel',
        })

    def do_progress(self):
        self.write({
            'status': 'progress',
        })

    def do_set_to(self):
        self.write({
            'status': ''
        })

    def open_check_in_url(self):
        if self.id:
            return {
                'type': 'ir.actions.act_url',
                'url': self.check_in_map_link,
                'target': 'new',
            }

    def open_check_out_url(self):
        if self.id:
            return {
                'type': 'ir.actions.act_url',
                'url': self.check_out_map_link,
                'target': 'new',
            }


