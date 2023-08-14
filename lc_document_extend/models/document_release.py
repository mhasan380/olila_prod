from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

class DocumentLetter(models.Model):
	_inherit = "document.release.letter"

	def _move_count(self):
		for rec in self:
			move_ids = self.env['account.move'].search([('lc_drl_id', '=', rec.id)])
			rec.move_count = len(move_ids.ids)

	def view_journal_entry(self):
		move_ids = self.env['account.move'].search([('lc_drl_id', '=', self.id)])
		return {
			'name': _('Journal Entries'),
			'view_type': 'form',
			'view_mode': 'tree,form',
			'res_model': 'account.move',
			'view_id': False,
			'type': 'ir.actions.act_window',
			'domain': [('id', 'in', move_ids.ids)],
		}

	lc_type = fields.Selection([('deferred', 'Deferred'), ('cash', 'Cash'), ('at_sight', 'At Sight')], string='LC Type' )
	ltr_number = fields.Char(string='LTR Number')
	accepted_bill_no = fields.Char(string='Accepted Bill No')
	move_count = fields.Integer(compute='_move_count', string='#Move')

	def button_confirm(self):
		for rec in self:
			if rec.lc_type:
				rec.write({'state': 'confirm'})
			else:
				raise ValidationError("Please select LC Type")

	def _prepare_move_line_at_sight(self):
		move_line_dict = []
		amount = 0.0
		vat_account = int(self.env['ir.config_parameter'].sudo().get_param(
			'lc_fund_req_journal.lc_vat_account'))
		tax_account = int(self.env['ir.config_parameter'].sudo().get_param(
			'lc_fund_req_journal.lc_fund_taxes'))
		bank = int(self.env['ir.config_parameter'].sudo().get_param(
			'lc_fund_req_journal.lc_opening_bank'))
		bank_account = self.env['account.journal'].search([('id', '=', bank)]).payment_credit_account_id.id
		transit_account = int(self.env['ir.config_parameter'].sudo().get_param(
			'lc_fund_req_journal.transit_account'))
		lc_outher_charges = int(self.env['ir.config_parameter'].sudo().get_param(
			'lc_fund_req_journal.lc_lcfr_other_charges'))
		ltr_account = int(self.env['ir.config_parameter'].sudo().get_param(
			'lc_fund_req_journal.ltr_account'))
		lc_margin_account = int(self.env['ir.config_parameter'].sudo().get_param(
			'lc_fund_req_journal.drl_margin_account'))
		if self.lc_open_id.total_amount != 0:
			margin_percent = self.total_amount / self.lc_open_id.total_amount
		else:
			margin_percent = 0
		mergin_amount = self.lc_open_id.requisition_id.margin * margin_percent
		ltr_amount = self.bdt_total + self.commission + self.postage + self.other_charges + self.source_tax + self.vat - self.margin - mergin_amount

		move_line_dict.append({
			'account_id': transit_account or False,
			'debit': self.bdt_total,
			# 'date_maturity': self.move_date,
			# 'date' : self.move_date,
		})
		move_line_dict.append({
			'account_id': lc_outher_charges or False,
			'debit': self.commission + self.postage+ self.other_charges,
			# 'date_maturity' : self.move_date,
			# 'date' : self.move_date,
		})
		move_line_dict.append({
			'account_id': tax_account or False,
			'debit': self.source_tax,
			# 'date_maturity' : self.move_date,
			# 'date' : self.move_date,
		})
		move_line_dict.append({
			'account_id': vat_account or False,
			'debit': self.vat,
			# 'date_maturity' : self.move_date,
			# 'date' : self.move_date,
		})
		move_line_dict.append({
			'account_id': bank_account or False,
			'credit': self.margin,
			# 'date_maturity' : self.move_date,
			# 'date' : self.move_date,
		})
		move_line_dict.append({
			'account_id': lc_margin_account or False,
			'credit': mergin_amount,
			# 'date_maturity' : self.move_date,
			# 'date' : self.move_date,
		})
		move_line_dict.append({
			'account_id': ltr_account or False,
			'credit': ltr_amount,
			'name' : self.ltr_number,
			# 'date' : self.move_date,
		})

		return move_line_dict

	def button_paid(self):
		for rec in self:
			move_lines1 = rec._prepare_move_line_at_sight()
			bank = int(self.env['ir.config_parameter'].sudo().get_param(
				'lc_fund_req_journal.lc_opening_bank'))
			bank_account = self.env['account.journal'].search([('id', '=', bank)]).payment_credit_account_id.id
			vals = {
				'move_type': 'entry',
				'date': rec.bl_date,
				'journal_id': rec.env['account.journal'].search([('id', '=', bank)],
																 limit=1).id,
				'line_ids': [(0, 0, line_data) for line_data in move_lines1]
			}
			move_id1 = self.env['account.move'].create(vals)
			move_id1.ref = 'Lc No' + rec.lc_open_id.lc_no
			move_id1.lc_drl_id = rec.id
			#Create LTR
			ltr_vals = {
						'lc_num': rec.lc_open_id.lc_no,
				        'lc_number': rec.lc_open_id.id,
						'number' : rec.ltr_number,
						'ltr_open_date': rec.bl_date,
						'ltr_creation' : rec.bdt_total,
						'ltr_account_id' : int(self.env['ir.config_parameter'].sudo().get_param('lc_fund_req_journal.ltr_account')),
						'bank_account_id': bank_account,
						'interest_account_id': int(self.env['ir.config_parameter'].sudo().get_param('lc_fund_req_journal.interest_account')),
						'bank_charge_id': int(self.env['ir.config_parameter'].sudo().get_param('lc_fund_req_journal.bank_charges')),


			}
			ltr_id = self.env['ltr.control'].create(ltr_vals)
			ltr_id.onchange_ltr_date()
			ltr_id.on_change_ltr_charges()
			ltr_id.overdue_status = 'run'
			rec.write({'state': 'paid'})




