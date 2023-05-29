# -*- coding: utf-8 -*-

from odoo import models,fields,api
from odoo.tools import date_utils
from odoo.exceptions import UserError, ValidationError

class DepotCommission(models.TransientModel):
    _name = 'depot.commission.report.wizard'
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
        return self.env.ref('depot_commission_report.depot_commission_report').report_action(self, data=data)

class DepotCommissionReport(models.AbstractModel):
    _name = 'report.depot_commission_report.depo_template'

    @api.model
    def _get_report_values(self, docids, data=None):
        model=self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        from_date=data['from_date']
        to_date=data['to_date']
        product_category=data['product_category']
        location_id = data['location_id']
        warehouse_id = data['warehouse_id']
        warehouse_name = self.env['stock.warehouse'].browse(warehouse_id)
        depo_commission=data['depo_commission']
        domain = [('scheduled_date', '>=', from_date), ('scheduled_date', '<=', to_date),('picking_type_code', '=', 'outgoing'),('state' ,'=','done'),('location_id' , '=' , location_id)]
        picking_ids= self.env['stock.picking'].search(domain)
        delivery_line_list = []
        discount_amount = 0
        sub_total = 0
        total_amount = 0
        total_qty = 0
        commission_amount = 0
        for delivery in picking_ids:
            delivery_total_amt = 0
            delivery_total_qty = 0
            for move in delivery.move_ids_without_package:
                discount_amount = (move.quantity_done * move.sale_line_id.price_unit) * move.sale_line_id.discount / 100
                sub_total = (move.quantity_done * move.sale_line_id.price_unit) - discount_amount
                delivery_total_amt += sub_total
                delivery_total_qty += move.quantity_done
            total_amount += delivery_total_amt
            total_qty += delivery_total_qty
            delivery_line_list.append({
                'name': delivery.name,
                'schedule_date': delivery.scheduled_date,
                'sale_id': delivery.origin,
                'delivery_address': delivery.partner_id.name,
                'delivery_total_amt': delivery_total_amt,
                'delivery_total_qty': delivery_total_qty,
            })
        commission_amount = (total_amount * depo_commission) / 100
        return {
            'docs': docs,
            'from_date': from_date,
            'to_date': to_date,
            'warehouse_id': warehouse_name.name,
            'total_amount': total_amount,
            'total_quantity':total_qty,
            'delivery_line_list': sorted(delivery_line_list,key=lambda l: l['schedule_date']),
            'depo_commission': depo_commission,
            'commission_amount': commission_amount,
        }




