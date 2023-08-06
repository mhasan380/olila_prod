from odoo import api, fields, models, _

class ExpenseNotebook(models.Model):
    _name = "expense.notebook"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Expense Notebook"
    date = fields.Date(string="Date", required=True, tracking=True)
    transaction_type = fields.Selection([
        ('payment', 'Payment'),
        ('receive', 'Receive'),
    ], default='receive', tracking=True, required=True)
    particular = fields.Text(string="Particular")
    amount = fields.Float(string="Amount", required=True, tracking=True)
    amount_signed = fields.Float(string="Balance", compute='_total_balance')
    payEE_receiver = fields.Text(string="Payee/Receiver")
    state = fields.Selection([
        ('draft', 'Draft'),
        ('confirm', 'confirmed'),
        ('cancel', 'Cancelled')], default='draft', string="status", tracking=True)
    reference_no = fields.Char(string='Reference', required=True, copy=False,
                               readonly=True, default=lambda self: _('New'))
    amount_word = fields.Char(string='Amount In Word', compute='_amount_in_word')
    operating_unit = fields.Selection([
        ('head office', 'Head Office'),
        ('factory', 'Factory')], default='head office', string="Operating_Unit", tracking=True)
    remarks = fields.Text(string="Remarks")

    def confirm_action(self):
        self.state = "confirm"

    def draft_action(self):
        self.state = "draft"

    def cancel_action(self):
        self.state = "cancel"

    @api.model
    def create(self, vals):
        if vals.get('reference_no', _('New')) == _('New'):
            vals['reference_no'] = self.env['ir.sequence'].next_by_code(
                'expense.notebook') or _('New')
        res = super(ExpenseNotebook, self).create(vals)
        return res

    @api.depends('amount')
    def _amount_in_word(self):
        self.amount_word = str(self.env.user.currency_id.amount_to_text(self.amount))
    @api.depends('amount', 'transaction_type','state')
    def _total_balance(self):
        for rec in self:
            if rec.state == 'confirm':
                if rec.transaction_type == 'receive':
                    rec.amount_signed = rec.amount
                else:
                    rec.amount_signed = rec.amount * (-1)
            else:
                rec.amount_signed = 0.0
    def print_expense_notebook(self):
        return self.env.ref('notebook.action_notebook_cash_voucher_report').report_action(self)
