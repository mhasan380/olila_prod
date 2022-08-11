# -*- coding: utf-8 -*-
import werkzeug
import requests
from odoo import models, fields, api
from odoo.addons import decimal_precision as dp


# UNIT = dp.get_precision("Location")
#
#
# def urlplus(url, params):
#     return werkzeug.Href(url)(params or None)


class CheckList(models.Model):
    _name = 'rode.list'
    name = fields.Char('Name')
    name_work = fields.Text('Task')
    description = fields.Text('Description')
    customer = fields.Many2one('res.partner', string='Customer')
    street = fields.Char(related='customer.street', string='Street')
    status = fields.Selection(string="Status",
                              selection=[('ready', 'Ready'), ('done', 'Done'), ('progress', 'In Progress'),
                                         ('cancel', 'Cancel')],
                              readonly=True)

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

    @api.model
    def create(self, vals):

        vals['status'] = 'ready'
        print(f'----------------{vals}')
        rec = super(CheckList, self).create(vals)

        return rec