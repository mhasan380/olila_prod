from odoo import models, fields, api


class ProductionWizard(models.TransientModel):
    _name = 'production.wizard'
    _description = 'Production Report'

    from_date = fields.Date(string="From Date")
    to_date = fields.Date(string="To Date")
    production_type = fields.Selection(
        [('pcs', 'PCS'), ('ei', 'Empty Inner'), ('emm', 'Empty Master'), ('fgi', 'FG Inner'), ('fgm', 'FG Master'),
         ('cullet', 'Cullet'), ('converstion', 'Conversion')])
    shift = fields.Selection([('a', 'A Shift'), ('b', 'B Shift'), ('c', 'C Shift')])
    product = fields.Many2one('product.product', string='Product')

    def get_report(self):
        data = {
            'ids': self.ids,
            'model': self._name,
            'form': {
                'production_type': self.production_type,
                'shift': self.shift,
                'product': self.product.name,
                'from_date': self.from_date,
                'to_date': self.to_date
            },
        }

        return self.env.ref('production_module_reports.production_report').report_action(self, data=data)


class ProductionReport(models.AbstractModel):
    _name = 'report.production_module_reports.prod_report_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        production_type = data['form']['production_type']
        shift = data['form']['shift']
        product = data['form']['product']
        from_date = data['form']['from_date']
        to_date = data['form']['to_date']
        production = []
        p_type = ''
        sh = ''

        domain = [('date_planned_start', '>=', from_date), ('date_planned_start', '<=', to_date)]
        if production_type:
            domain.append(('production_type', '=', production_type))


        if product:
            domain.append(('product_id', '=', product))
        if shift:
            domain.append(('shift', '=', shift))

        documents = self.env['mrp.production'].search(domain)

        for orders in documents:

            if orders.production_type == 'pcs':
                p_type = 'PCS'
            elif orders.production_type == 'ei':
                p_type = 'Empty Inner'
            elif orders.production_type == 'emm':
                p_type = 'Empty Master'
            elif orders.production_type == 'fgi':
                p_type = 'FG Inner'
            elif orders.production_type == 'fgm':
                p_type = 'FG Master'
            elif orders.production_type == 'cullet':
                p_type = 'Cullet'
            else:
                p_type = 'Conversion'
            production.append({
                'name': orders.name,
                'date': orders.date_planned_start,
                'production_type': p_type,
                'shift': orders.shift,
                'cullet_type': orders.cullet_type,
                'product_code': orders.product_id.default_code,
                'product_name': orders.product_id.name,
                'qty': orders.product_qty,
                'uom': orders.product_id.uom_id.name,
                'avg_weight': orders.average_weight,
                'total_weight': orders.total_weight,
                'state': orders.state,
                'responsible': orders.user_id.name
            })
        return {
            'doc_ids': data.get('ids'),
            'doc_model': data.get('model'),
            'from_date': from_date,
            'to_date': to_date,
            'production_type': production_type,
            'p_type': p_type,
            'shift': shift,
            'sh': sh,
            'product': product,
            'production': production
        }
