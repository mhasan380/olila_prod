# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils
from odoo.exceptions import UserError, ValidationError
from num2words import num2words

class DepotProdCommission(models.TransientModel):
    _name = 'depot.product.com.wizard'
    from_date = fields.Date(string="Date From", required=True)
    to_date = fields.Date(string="Date To", required=True)
    product_category = fields.Many2one('product.category', string="Category")
    warehouse_id = fields.Many2one('stock.warehouse', string="Depot Name",required=True)
    depo_commission=fields.Float(string="Commission%",required=True)

    @api.constrains('to_date')
    def _check_date(self):
        if self.from_date and self.to_date and self.from_date > self.to_date:
            raise ValidationError("From Date must be less than To Date")

    def get_report(self):
        data = {
            'from_date':self.from_date,
            'to_date':self.to_date,
            'product_category':self.product_category.id,
            'warehouse_id': self.warehouse_id.id,
            'location_id': self.warehouse_id.lot_stock_id.id,
            'depo_commission': self.depo_commission,
        }
        return self.env.ref('depot_commission_report.depot_product_report').report_action(self, data=data)

class DepotprodCommissionReport(models.AbstractModel):
    _name = 'report.depot_commission_report.deport_prod_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model=self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        from_date=data['from_date']
        to_date=data['to_date']
        product_category = data['product_category']
        location_id = data['location_id']
        warehouse_id = data['warehouse_id']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)
        depo_commission=data['depo_commission']
        domain = [('picking_id.scheduled_date', '>=', from_date), ('picking_id.scheduled_date', '<=', to_date),('picking_id.picking_type_code', '=', 'outgoing'),('picking_id.state' ,'=','done'),('location_id' , '=' , location_id)]
        if product_category:
            domain.append(('product_id.categ_id', '=', product_category))
        moves = self.env['stock.move'].search(domain)
        discount_amount = 0
        sub_total = 0
        total_amount = 0
        total_qty = 0
        total_commission = 0
        list2 = []
        product_wise_lines = {}
        for line in moves:
            if line.product_id in product_wise_lines:
                product_wise_lines[line.product_id] |= line
            else:
                product_wise_lines[line.product_id] = line
        total_qty = 0.0
        for product, lines in product_wise_lines.items():
            product_total = 0
            for line in lines:
                discount_amount = (line.product_uom_qty * line.sale_line_id.price_unit) * line.sale_line_id.discount / 100
                sub_total = (line.product_uom_qty * line.sale_line_id.price_unit) - discount_amount
                product_total += sub_total
            net_comission = (product_total * depo_commission) / 100
            list2.append({
                'product_code': product.default_code or '',
                'product_name': product.name,
                'product_qty': sum(lines.mapped('product_uom_qty')),
                'net_value': product_total,
                'com_percent': depo_commission,
                'net_comission': net_comission,
                'uom' : product.uom_id.name
            })
            total_qty += sum(lines.mapped('product_uom_qty'))
            total_amount += product_total
            total_commission += net_comission
            word_num = str(self.env.user.currency_id.amount_to_text(total_commission))
        return {
            'docs': docs,
            'from_date': from_date,
            'to_date': to_date,
            'warehouse': warehouse_name,
            'total_amount': total_amount,
            'total_quantity':total_qty,
            'list2': sorted(list2,key=lambda l: l['product_code']),
            'total_commission': total_commission,
            'word_num' : word_num
        }



