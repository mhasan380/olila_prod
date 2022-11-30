from odoo import api, fields, models
from datetime import date


class Planning(models.Model):
    _name = 'sales.person.plan'
    _description = 'Sales Person Daily Planning'
    _rec_name = 'name'

    name = fields.Char('Name')
    # user_id = fields.Many2one('res.users', string="Assigned User", default=lambda self: self.env.user, )

    partner_id = fields.Many2one('res.partner', 'Customer Name')
    customer = fields.Many2one('res.partner', string='Customer name')
    street = fields.Char(related='customer.street', string='Customer Street')
    sales_plan_date = fields.Date('Plan Date & Time', default=date.today())
    end_plan_date = fields.Date('End Date & Time', default=date.today())
    assigned_by = fields.Many2one('hr.employee', string='Assigned by')
    assigned_to = fields.Many2one('hr.employee', string='Assigned to')

    state = fields.Selection([
        ('planned', 'Planned'),
        ('progress', 'Progress'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
    ], copy=False, default="planned")
    check_box = fields.Boolean(string='Is Rode List', default=True)
    info_checklist = fields.One2many("rode.list",'route_id', required=True,
                                     track_visibility='onchange')
    progress_rate = fields.Integer(string='Road list Progress', compute="check_rate")
    total = fields.Integer(string="Max")
    status = fields.Selection(string="Status",
                              selection=[('done', 'Done'), ('progress', 'In Progress'), ('cancel', 'Cancel')],
                              readonly=True, track_visibility='onchange')

    maximum_rate = fields.Integer(default=100)
    check_in_latitude = fields.Float(
        "Check-in Latitude", digits="Location", readonly=True
    )
    check_in_longitude = fields.Float(
        "Check-in Longitude", digits="Location", readonly=True
    )


    def check_rate(self):
        for rec in self:
            rec.progress_rate = 0
            total = len(rec.info_checklist.ids)
            done = 0
            cancel = 0
            # message = 'Create Work!'
            if total == 0:
                pass
            else:
                if rec.info_checklist:
                    for item in rec.info_checklist:
                        if item.status == 'done':
                            done += 1
                            # message = "Work: %s <br> Status: done" % (item.name_work)
                        if item.status == 'cancel':
                            cancel += 1
                            # message = "Work: %s <br> Status: cancel" % (item.name_work)
                        # if item.status == 'progress':
                        #     message = "Work: %s <br> Status: In Progress" % (item.name_work)
                    if cancel == total:
                        rec.progress_rate = 0
                    else:
                        rec.progress_rate = round(done / (total - cancel), 2) * 100

    def action_progress(self):
        self.state = 'progress'

    def action_done(self):
        self.state = 'done'

    def action_cancel(self):
        self.state = 'cancel'
