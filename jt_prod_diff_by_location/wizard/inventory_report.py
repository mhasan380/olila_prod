# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-Today Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

from odoo import api, fields, models
from datetime import datetime, timedelta


class InventoryReport(models.Model):

    _name = 'inventory.report'
    _description = "Inventory Report"

    company_ids = fields.Many2many('res.company',
                                   'inventory_rep_company_rel',
                                   'inv_id',
                                   'company_id',
                                   "Company",
                                   help="You can select multiple companies, \
                                       if you are not selecting any company \
                                       than it will prepare result for \
                                       all companies")
    warehouse_ids = fields.Many2many('stock.warehouse',
                                     'inventory_rep_warehouse_rel',
                                     'inv_id',
                                     'warehouse_id',
                                     "Warehouse",
                                     help="You can select multiple warehouse, \
                                         if you are not selecting any than it \
                                         will prepare result for all \
                                         warehouses")
    start_date = fields.Date("Start Date",
                             help="Select Start date which is mandatory \
                                 field for period range")
    end_date = fields.Date("End Date",
                           help="Select end date which is mandatory field \
                               for period range")
    product_category_ids = fields.Many2many('product.category',
                                            'inventory_product_categ_rel',
                                            'inv_id',
                                            'product_categ_id',
                                            string="Product Category")
    product_ids = fields.Many2many("product.product",
                                   "inventory_product_rel",
                                   "inv_id",
                                   "product_id",
                                   string="Product")
    with_zero_info = fields.Boolean("Include Zero Transaction Data?")

    # @api.multi
    def print_inventory_report(self):
        """
             To print report.
             @param self: The object pointer.
             @return: Report action
        """

        self.ensure_one()
        return self.env.ref('jt_prod_diff_by_location.inventory_report_stock').report_action(self.env.context.get('active_ids', []))

    def _get_received_delivered_products(self, location_id, product,
                                         start_date, end_date):

        cr = self._cr
        cr.execute("select sum(qty) from stock_quant where product_id=%s \
            and location_id=%s and in_date >=%s and in_date<=%s",
                   (product.id, location_id, start_date, end_date))
        q_result = cr.fetchone()
        if q_result[0] is not None:
            return q_result[0]
        else:
            return 0.0

    def _get_adjusted_qty(self, product_id, warehouse_id, start_date, end_date):

        ad_in_qty = 0.0
        ad_out_qty = 0.0

        cr = self._cr
        cr.execute("select sum(product_uom_qty) from stock_move where \
            product_id=%s and state='done' and date>=%s and date<=%s and \
            picking_type_id is null and location_dest_id = \
            (select default_location_dest_id from stock_picking_type \
            where warehouse_id=%s and code=%s and name=%s)",
                   (product_id, start_date, end_date, warehouse_id,
                    'incoming', 'Receipts'))
        adjust_in_qty = cr.fetchone()
        if adjust_in_qty[0] is not None:
            ad_in_qty = adjust_in_qty[0]

        cr.execute("select sum(product_uom_qty) from stock_move where \
            product_id=%s and state='done' and date>=%s and date<=%s and \
            picking_type_id is null and location_id = (select \
            default_location_src_id from stock_picking_type where \
            warehouse_id=%s and code=%s and name=%s)",
                   (product_id, start_date, end_date, warehouse_id,
                    'outgoing', 'Delivery Orders'))
        adjust_out_qty = cr.fetchone()
        if adjust_out_qty[0] is not None:
            ad_out_qty = adjust_out_qty[0]
        adjustment_qty = ad_in_qty - ad_out_qty

        return adjustment_qty

    def _get_openning_stock(self, product_id, warehouse_id, start_date):

        in_qty = 0.0
        out_qty = 0.0
        ad_in_qty = 0.0
        ad_out_qty = 0.0
        cr = self._cr
        cr.execute("select sum(product_uom_qty) from stock_move where \
            product_id=%s and state='done' and date<=%s and picking_type_id is \
            null and location_dest_id = (select default_location_dest_id \
            from stock_picking_type where warehouse_id=%s and code=%s \
            and name=%s)",
                   (product_id, start_date, warehouse_id, 'incoming', 'Receipts'))

        adjust_in_qty = cr.fetchone()
        if adjust_in_qty[0] is not None:
            ad_in_qty = adjust_in_qty[0]
            return ad_in_qty
        cr.execute("select sum(product_uom_qty) from stock_move \
            where product_id=%s and state='done' and date<=%s and \
            picking_type_id is null and location_id = (select \
            default_location_src_id from stock_picking_type where \
            warehouse_id=%s and code=%s and name=%s)",
                   (product_id, start_date, warehouse_id,
                    'outgoing', 'Delivery Orders'))
        adjust_out_qty = cr.fetchone()
        if adjust_out_qty[0] is not None:
            ad_out_qty = adjust_out_qty[0]
        cr.execute("select sum(product_uom_qty) from stock_move where \
            product_id=%s and state='done' and date<%s and picking_type_id \
            = (select id from stock_picking_type where warehouse_id=%s and \
            code=%s and name=%s)",
                   (product_id, start_date, warehouse_id, 'incoming', 'Receipts'))
        opening_in_qty = cr.fetchone()
        if opening_in_qty[0] is not None:
            in_qty = opening_in_qty[0]
        cr.execute("select sum(product_uom_qty) from stock_move where \
            product_id=%s and state='done' and date<%s and picking_type_id \
            = (select id from stock_picking_type where warehouse_id=%s and \
            code=%s and name=%s)",
                   (product_id, start_date, warehouse_id,
                    'outgoing', 'Delivery Orders'))
        opening_out_qty = cr.fetchone()
        if opening_out_qty[0] is not None:
            out_qty = opening_out_qty[0]
        opening_stock = (in_qty + ad_in_qty) - (out_qty + ad_out_qty)

        return opening_stock

    def _get_product_in_info(self, product_id, warehouse_id, start_date,
                             end_date, usage, code, name):
        cr = self._cr
        cr.execute("select sum(product_uom_qty) from \
            stock_move where product_id=%s and state='done' and date>=%s \
            and date<=%s and origin_returned_move_id is null and \
            location_dest_id in (select id from stock_location where \
            usage='internal') and warehouse_id=%s",
                   (product_id, start_date, end_date, warehouse_id))
        result = cr.fetchone()
        if result[0] is not None:
            return result[0]
        else:
            return 0.0

    def _get_product_info(self, product_id, warehouse_id, start_date,
                          end_date, usage, code, name):
        cr = self._cr
        cr.execute("select sum(product_uom_qty) from stock_move where \
            product_id=%s and state='done' and date>=%s and date<=%s and \
            location_dest_id in (select id from stock_location where \
            usage=%s) and picking_type_id = (select id from \
            stock_picking_type where warehouse_id=%s and \
            code=%s and name=%s)",
                   (product_id, start_date, end_date, usage, warehouse_id, code, name))
        result = cr.fetchone()
        if result[0] is not None:
            return result[0]
        else:
            return 0.0

    def _get_return_in_qty(self, product_id, warehouse_id, start_date,
                           end_date, code, name):
        cr = self._cr
        cr.execute("select sum(product_uom_qty) from stock_move where \
            product_id=%s and state='done' and date>=%s and date<=%s and \
            origin_returned_move_id is not null and location_dest_id in \
            (select id from stock_location where usage='internal') and \
            warehouse_id=%s", (product_id, start_date, end_date, warehouse_id))
        result = cr.fetchone()
        if result[0] is not None:
            return result[0]
        else:
            return 0.0

    def _get_return_out_qty(self, product_id, warehouse_id, start_date,
                            end_date, code, name):
        cr = self._cr
        cr.execute("select sum(product_uom_qty) from stock_move \
            where product_id=%s and state='done' and date>=%s and date<=%s \
            and origin_returned_move_id is not null and location_dest_id \
            in (select id from stock_location where usage='supplier') and \
            warehouse_id=%s", (product_id, start_date, end_date, warehouse_id))
        result = cr.fetchone()
        if result[0] is not None:
            return result[0]
        else:
            return 0.0

    def _get_product_detail(self, company_id, warehouse_id, product_categ_id,
                            obj):
        product_obj = self.env['product.product']
        final_data = []
        product_ids = obj.product_ids
        include_zero_trans = obj.with_zero_info
        start_date = obj.start_date
        end_date = obj.end_date
        if start_date and end_date and warehouse_id:
            if product_ids and product_categ_id:
                final_product_ids = product_obj.search([('categ_id',
                                                         '=',
                                                         product_categ_id),
                                                        ('id',
                                                         'in',
                                                         product_ids.ids)])
            elif not product_categ_id and product_ids:
                final_product_ids = product_ids
            elif product_categ_id and not product_ids:
                final_product_ids = product_obj.search([('categ_id',
                                                         '=',
                                                         product_categ_id)])
            else:
                final_product_ids = product_obj.search([])
            if final_product_ids:
                for product in final_product_ids:
                    data = {}
                    opening_qty = self._get_openning_stock(product.id,
                                                           warehouse_id,
                                                           start_date)
                    data.update({'opening': opening_qty})
                    delivered_qty = self._get_product_info(product.id,
                                                           warehouse_id,
                                                           start_date,
                                                           end_date,
                                                           'customer',
                                                           'outgoing',
                                                           'Delivery Orders')
                    data.update({'delivered_product': delivered_qty})
                    received_qty = self._get_product_in_info(product.id,
                                                             warehouse_id,
                                                             start_date,
                                                             end_date,
                                                             'internal',
                                                             'incoming',
                                                             'Receipts')
                    data.update({'received_product': received_qty})
                    return_in_qty = self._get_return_in_qty(product.id,
                                                            warehouse_id,
                                                            start_date,
                                                            end_date,
                                                            'outgoing',
                                                            'Delivery Orders')
                    data.update({'return_in_qty': return_in_qty})
                    return_out_qty = self._get_return_out_qty(product.id,
                                                              warehouse_id,
                                                              start_date,
                                                              end_date,
                                                              'incoming',
                                                              'Receipts')
                    data.update({'return_out_qty': return_out_qty})
                    internal_qty = self._get_product_info(product.id,
                                                          warehouse_id,
                                                          start_date,
                                                          end_date,
                                                          'internal',
                                                          'internal',
                                                          'Internal Transfers')
                    data.update({'internal_qty': internal_qty})
                    adjusted_qty = self._get_adjusted_qty(product.id,
                                                          warehouse_id,
                                                          start_date,
                                                          end_date)
                    data.update({'adjusted_qty': adjusted_qty})
                    data.update({'product_name': product.display_name})
                    if include_zero_trans:
                        final_data.append(data)
                    elif received_qty > 0 or delivered_qty > 0 or \
                        internal_qty > 0 or adjusted_qty > 0 or adjusted_qty < 0 \
                            or opening_qty > 0 or opening_qty < 0 or return_in_qty > 0 \
                            or return_out_qty > 0:
                        final_data.append(data)
                    else:
                        continue
            return final_data

    def _get_product_categories(self, product_categ_ids, product_ids):

        if not product_ids and not product_categ_ids:
            return self.env['product.category'].search([])
        elif product_ids and not product_categ_ids:
            prod_categ_ids = [product.categ_id for product in product_ids]
            prod_categ_ids = list(set(prod_categ_ids))
            return prod_categ_ids
        elif product_categ_ids and not product_ids:
            return product_categ_ids
        else:
            return self.env['product.category'].search([])

    def _get_companies(self, company_ids):
        if company_ids:
            return company_ids
        return self.env['res.company'].search([])

    def _get_warehouses(self, warehouse_ids, company_id):

        warehouse_obj = self.env['stock.warehouse']
        if warehouse_ids:
            return warehouse_obj.search([('id', 'in', warehouse_ids.ids),
                                         ('company_id', '=', company_id.id)])
        return warehouse_obj.search([('company_id', '=', company_id.id)])


