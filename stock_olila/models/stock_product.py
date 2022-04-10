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
    rack_id = fields.Many2one('stock.rack', string='Rack')
    fs_type = fields.Selection([('pcs', 'PCS'), ('inner', 'Inner'), ('master', 'Master')],string='FS Goods Type')
    mctn_qty = fields.Float(compute="_compute_mctn_qty",string='Master Carton Qty', search='_search_mctn_qty')
    undelivered_mctn = fields.Float(compute="_compute_undelivered_mctn",string='Undelivered MCTN', search='_search_undelivered_mctn')
    total_weight = fields.Float(compute="_compute_total_weight", string='Total Weight', search='_search_total_weight')
    net_value = fields.Float(compute="_compute_net_value", string='Net value', search='_search_net_value')

    @api.depends('lst_price', 'net_stock')
    def _compute_net_value(self):
        for product in self:
            product.net_value = product.lst_price * product.net_stock

    @api.depends('qty_available', 'weight')
    def _compute_total_weight(self):
        for product in self:
            product.total_weight = product.qty_available * product.weight

    @api.depends('outgoing_qty', 'fs_type')
    def _compute_undelivered_mctn(self):
        for product in self:
            if product.fs_type == 'pcs':
                product.undelivered_mctn = product.outgoing_qty / 72
            elif product.fs_type == 'inner':
                product.undelivered_mctn = product.outgoing_qty /12
            elif product.fs_type == 'master':
                product.undelivered_mctn = product.outgoing_qty
            else:
                product.undelivered_mctn = 0

    @api.depends('qty_available', 'fs_type')
    def _compute_mctn_qty(self):
        for product in self:
            if product.fs_type == 'pcs':
                product.mctn_qty = product.qty_available / 72
            elif product.fs_type == 'inner':
                product.mctn_qty = product.qty_available / 12
            elif product.fs_type == 'master':
                product.mctn_qty = product.qty_available
            else:
                product.mctn_qty = 0

    @api.depends('qty_available','outgoing_qty','fs_type')
    def _compute_net_qty(self):
        for product in self:
            if product.fs_type == 'master':
                product.net_stock = product.qty_available - product.outgoing_qty
            elif product.fs_type == 'pcs':
                product.net_stock = product.mctn_qty - (product.outgoing_qty / 72 )
            elif product.fs_type == 'inner':
                product.net_stock = product.mctn_qty - (product.outgoing_qty / 12 )
            else:
                product.net_stock = 0

    @api.depends('qty_available', 'lst_price')
    def _compute_sale_price_total(self):
        for product in self:
            product.sales_price_total = product.qty_available * product.lst_price

    def _search_net_stock(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_total_quantity(operator, value, 'net_stock')
    def _search_sales_price_total(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_total_quantity(operator, value, 'sales_price_total')
    def _search_mctn_qty(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_total_quantity(operator, value, 'mctn_qty')
    def _search_total_weight(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_total_quantity(operator, value, 'total_weight')
    def _search_net_value(self, operator, value):
        # TDE FIXME: should probably clean the search methods
        return self._search_product_total_quantity(operator, value, 'net_value')

    def _search_product_total_quantity(self, operator, value, field):
        # TDE FIXME: should probably clean the search methods
        # to prevent sql injections
        if field not in ('net_stock','sales_price_total','mctn_qty','undelivered_mctn','total_weight','net_value'):
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
        if 'qty_available' or 'net_stock' or 'outgoing_qty' or 'sales_price_total' or 'mctn_qty' or 'undelivered_mctn' or 'total_weight' or 'net_value' in fields:
            for line in res:
                if '__domain' in line:
                    lines = self.search(line['__domain'])
                    total_product_qty = 0.0
                    total_net_qty = 0.0
                    total_out_qty = 0.0
                    total_sale_price = 0.0
                    total_mctn_qty = 0.0
                    total_undelivered_mctn = 0.0
                    total_product_weight = 0.0
                    total_net_value = 0.0
                    for record in lines:
                        total_product_qty += record.qty_available
                        total_net_qty += record.net_stock
                        total_out_qty += record.outgoing_qty
                        total_sale_price += record.sales_price_total
                        total_mctn_qty += record.mctn_qty
                        total_undelivered_mctn += record.undelivered_mctn
                        total_product_weight += record.total_weight
                        total_net_value += record.net_value

                    line['qty_available'] = total_product_qty
                    line['net_stock'] = total_net_qty
                    line['outgoing_qty'] = total_out_qty
                    line['sales_price_total'] = total_sale_price
                    line['mctn_qty'] = total_mctn_qty
                    line['undelivered_mctn'] = total_undelivered_mctn
                    line['total_weight'] = total_product_weight
                    line['net_value'] = total_net_value

        return res


class StoreRack(models.Model):
    _name = 'stock.rack'
    _inherit = ['format.address.mixin', 'mail.thread', 'mail.activity.mixin']
    _description = 'Rack'

    name = fields.Char('Rack Number')
    description = fields.Char('Description')

    _sql_constraints = [
        ('unique_name',
         'unique(name)',
         'A Rack already exists with this name .Rack name must be unique!')]
    


