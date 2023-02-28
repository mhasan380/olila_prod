from odoo import api, fields, models


class DailyProjection(models.Model):
    _name = 'daily.projection'
    _description = 'Daily Projection'

    @api.onchange('region')
    def on_change_region(self):
        if self.region:
            self.responsible = self.region.responsible.id
            self.target_amount = self.region.responsible.target
            return {'domain': {'territory': [('zone_id', '=', self.region.id)]}}

    @api.onchange('territory')
    def on_change_territory(self):
        if self.territory:
            self.responsible = self.territory.responsible.id
            self.target_amount = self.territory.responsible.target
            return {'domain': {'so_market': [('territory_id', '=', self.territory.id)]}}

    @api.onchange('so_market')
    def on_change_so_market(self):
        if self.so_market:
            self.responsible = self.so_market.responsible.id
            self.target_amount = self.so_market.responsible.target

    date = fields.Date(string="Date", required=True)
    region = fields.Many2one('res.zone', string="Region", required=True)
    territory = fields.Many2one('route.territory', string="Territory")
    so_market = fields.Many2one('route.area', string="SO Market")
    responsible = fields.Many2one('hr.employee', string="Responsible")
    customer = fields.Many2one('res.partner', string="Customer")
    target_amount = fields.Float(string="Target Amount")
    projection_amount = fields.Float(string="Projection Amount")
    projection_percentage = fields.Float(string="Projection %", compute="_percent_calculation")
    ref = fields.Char(string="Reference")

    @api.model
    def create(self, vals):
        vals['ref'] = self.env['ir.sequence'].next_by_code('daily.projection')
        return super(DailyProjection, self).create(vals)

    @api.depends('projection_amount', 'target_amount')
    def _percent_calculation(self):
        for record in self:
            if record.target_amount != 0:
                record.projection_percentage = (record.projection_amount / record.target_amount) * 100
            else:
                record.projection_percentage = 0

    # @api.depends('region')
    # def _compute_territory_domain(self):
    #     for rec in self:
    #         rec.territory_domain = json.dumps([('region', '=', rec.region.id)])
    #
    # @api.depends('territory')
    # def _compute_so_market_domain(self):
    #     for rec in self:
    #         rec.so_market_domain = json.dumps([('territory', '=', rec.territory.id)])
