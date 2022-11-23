from odoo import models, fields, api


class PaymentCollectionWizard(models.TransientModel):
    _name = 'payment.collection.wizard'
    _description = 'Payment Collection Report'

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    so_type = fields.Selection([('retail', 'Retail'), ('corporater', 'Corporate')], string="Customer Type")
    bank_name = fields.Many2one('account.journal', string='Bank')
    responsible = fields.Many2one('hr.employee', string='Responsible')
    status = fields.Selection([('draft', 'Draft'), ('posted', 'Posted'), ('cancel', 'Cancelled')])

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'so_type': self.so_type,
                'bank_name': self.bank_name.id,
                'responsible': self.responsible.name,
                'from_date': self.from_date,
                'to_date': self.to_date,
                'status': self.status
            },
        }

        return self.env.ref('internal_transfer_summary_report.payment_collection_report').report_action(self, data=data)


class PaymentCollectionReport(models.AbstractModel):
    _name = 'report.internal_transfer_summary_report.payment_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        so_type = data['form']['so_type']
        bank_name = data['form']['bank_name']
        responsible = data['form']['responsible']
        status = data['form']['status']
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        payment_list = []

        domain = [('date', '>=', from_date), ('date', '<=', to_date), ('partner_type', '=', 'customer')]
        if so_type:
            if so_type == 'retail':
                domain.append(('partner_id.olila_type', '=', ('dealer', 'distributor')))
            elif so_type == 'corporater':
                domain.append(('partner_id.olila_type', '=', 'corporater'))
        if bank_name:
            domain.append(('journal_id', '=', bank_name))
        if responsible:
            domain.append(('responsible_id', '=', responsible))
        if status:
            domain.append(('state', '=', status))

        documents = self.env['account.payment'].search(domain)
        print(documents)

        for payments in documents:
            payment_list.append({
                'date': payments.date,
                'bank_name': payments.journal_id.name,
                'customer': payments.partner_id.name,
                'responsible': payments.responsible_id.name,
                'amount': payments.amount,
                'status': payments.state
            })
        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'from_date': from_date,
            'to_date': to_date,
            'so_type': so_type,
            'bank_name': bank_name,
            'responsible': responsible,
            'status': status,
            'payment_list': payment_list
        }
