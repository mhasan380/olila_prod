import operator as py_operator

from odoo import api, fields, models, _
from odoo.exceptions import UserError

OPERATORS = {
    '<': py_operator.lt,
    '>': py_operator.gt,
    '<=': py_operator.le,
    '>=': py_operator.ge,
    '=': py_operator.eq,
    '!=': py_operator.ne
}

class ProductTemplate(models.Model):
    _inherit = 'product.product'

    net_stock = fields.Float(compute="_compute_net_qty",string='Net Stock', search='_search_net_stock' )
    sales_price_total = fields.Float(compute="_compute_sale_price_total", string='Total Sales Price',search='_search_sales_price_total')
    goods_type = fields.Selection([('finish', 'Finished Goods'), ('spare', 'Spare Parts'), ('raw', 'Raw Materials')],string='Goods Type')


    @api.depends('qty_available','outgoing_qty')
    def _compute_net_qty(self):
        for product in self:
            product.net_stock = product.qty_available - product.outgoing_qty

    @api.depends('qty_available', 'lst_price')
    def _compute_sale_price_total(self):
        for product in self:
            product.sales_price_total = product.qty_available * product.lst_price

    def _search_net_stock(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_quantity(operator, value, 'net_stock')
    def _search_sales_price_total(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_quantity(operator, value, 'sales_price_total')

    def _search_product_quantity(self, operator, value, field):
        # TDE FIXME: should probably clean the search methods
        # to prevent sql injections
        if field not in ('net_stock','sales_price_total'):
            raise UserError(_('Invalid domain left operand %s', field))
        if operator not in ('<', '>', '=', '!=', '<=', '>='):
            raise UserError(_('Invalid domain operator %s', operator))
        if not isinstance(value, (float, int)):
            raise UserError(_('Invalid domain right operand %s', value))

        # TODO: Still optimization possible when searching virtual quantities
        ids = []
        # Order the search on `id` to prevent the default order on the product name which slows
        # down the search because of the join on the translation table to get the translated names.
        for product in self.with_context(prefetch_fields=False).search([], order='id'):
            if OPERATORS[operator](product[field], value):
                ids.append(product.id)
        return [('id', 'in', ids)]


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





    

                
