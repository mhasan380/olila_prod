from odoo import api, fields, models, _

class Picking(models.Model):
    _inherit = "stock.picking"

    is_lc = fields.Boolean('IS LC?')
    lc_no = fields.Char('LC No')
    be_no = fields.Char('BE No')
    pi_no = fields.Char('PI No')
    landing = fields.Char('Port of landing')
    cnf = fields.Many2one('res.partner', string="CNF Agent")
    suplier_name = fields.Text('Supplier')
    purchase_type = fields.Selection([('local', 'Local'), ('import', 'Import')])
    purchased_by = fields.Many2one('res.users', string="Purchased By")

    # @api.model
    # def create(self, vals):
    #     res = super(Picking, self).create(vals)
    #     # import pdb;pdb.set_trace();
    #     if vals.get('picking_type_code') == 'incoming':
    #         print('This is done')
    #         # purchase_order = self.env['purchase.order'].search([('name', '=', vals.get('origin'))], limit=1)
    #         # res['suplier_name'] = purchase_order.remark
    #         # res['purchase_type'] = purchase_order.purchase_type
    #         # res['purchased_by'] = purchase_order.user_id.id
    #         # res['requestion_number'] = purchase_order.origin
    #     return res


