from odoo import models, fields, api


class DoReportWizard(models.TransientModel):
    _name = 'do.report.wizard'
    _description = 'Do Print Report'

    sale_order = fields.Many2one('sale.order', string="Sale Order")

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'so_id': self.sale_order.id,

            },
        }

        return self.env.ref('internal_transfer_summary_report.do_print_report').report_action(self, data=data)


class DoPrintReport(models.AbstractModel):
    _name = 'report.internal_transfer_summary_report.do_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        so_id = data['form']['so_id']

        sale_order = self.env['sale.order'].search([('id','=',so_id)])

        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'sale_order': sale_order,

        }
