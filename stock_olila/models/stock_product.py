from odoo import api, fields, models

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    net_stock = fields.Float(compute="_compute_net_qty",string='Net Stock')
    sales_price_total = fields.Float(compute="_compute_sale_price_total", string='Total Sales Price')

    @api.depends('qty_available','outgoing_qty')
    def _compute_net_qty(self):
        for product in self:
            product.net_stock = product.qty_available - product.outgoing_qty

    @api.depends('qty_available', 'lst_price')
    def _compute_sale_price_total(self):
        for product in self:
            product.sales_price_total = product.qty_available * product.lst_price


    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(ProductTemplate, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby,
                                                 lazy=lazy)
        if 'qty_available' or 'net_stock' or 'outgoing_qty' or 'sales_price_total' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_product_qty = 0.0
                    total_net_qty = 0.0
                    total_out_qty = 0.0
                    total_sale_price = 0.0
                    for record in lines:
                        total_product_qty += record.qty_available
                        total_net_qty += record.net_stock
                        total_out_qty += record.outgoing_qty
                        total_sale_price += record.sales_price_total

                    line['qty_available'] = total_product_qty
                    line['net_stock'] = total_net_qty
                    line['outgoing_qty'] = total_out_qty
                    line['sales_price_total'] = total_sale_price

        return res





    

                
