from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"

    do_date = fields.Datetime('DO Date')
    department_id = fields.Many2one('hr.department', string='Department')
    receiver = fields.Char('Received By')

    @api.model
    def create(self, vals):
        res = super(Picking, self).create(vals)
        # import pdb;pdb.set_trace();
        if vals.get('origin'):
            sale_order = self.env['sale.order'].search([('name', '=', vals.get('origin'))], limit=1)
            res['do_date'] = sale_order.date_order
        return res




class Warehouse(models.Model):
    _inherit = "stock.warehouse"

    is_depot = fields.Boolean('Depot')