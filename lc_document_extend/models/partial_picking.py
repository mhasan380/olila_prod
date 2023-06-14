from odoo import api, fields, models, _

class PartialPicking(models.TransientModel):
    _inherit = 'partial.picking.wizard'

    def create_move_to_picking(self, stock_move_obj):
        cnf_id = self.env['res.cf.aggent'].search([('document_release_letter_id', '=', self.release_letter_id.id),
                                                                            ('state','=', 'paid')], limit=1)
        stock_move_ids = stock_move_obj._action_confirm()
        stock_move_ids.picking_id.purchase_id = self.release_letter_id.lc_open_id and self.release_letter_id.lc_open_id.order_id and self.release_letter_id.lc_open_id.order_id.id
        stock_move_ids.picking_id.release_letter_id = self.release_letter_id and self.release_letter_id.id
        stock_move_ids.picking_id.is_lc = True
        stock_move_ids.picking_id.lc_no = self.release_letter_id.lc_open_id.lc_no
        stock_move_ids.picking_id.be_no = cnf_id.be_no
        stock_move_ids.picking_id.pi_no = self.release_letter_id.lc_open_id.order_id.partner_ref
        stock_move_ids.picking_id.landing = self.release_letter_id.lc_open_id.port_of_landing
        stock_move_ids.picking_id.cnf = cnf_id.aggent_partner_id.id
        stock_move_ids._action_assign()
        # order_id = self.lines_ids.mapped('po_line_id').mapped('order_id')
        # for picking in stock_move_ids.mapped('picking_id'):
        #     picking.partner_id = order_id.partner_id.id if order_id.partner_id else False
        return True