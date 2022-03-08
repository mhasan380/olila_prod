# -*- coding: utf-8 -*-
{
    'name': "Total stock and Net Stock",
    'summary': """Stock Product Sale""",
    'description': """Stock Product Sale Details""",
    'author': "Preciseways",
    'website': "http://www.preciseways.com",
    'version': '14.0',
    'depends': ['sale_management','stock', 'sale_stock', 'fleet', 'hr','purchase_request','olila_distribution'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_product.xml',
        'views/stock_picking.xml',
        'views/store_rack.xml',
        'reports/material_recieve_report.xml',
        'reports/depot_stock_report_view.xml',
        'reports/raw_stock_report_view.xml',
        'wizard/depot_stock_report_wizard_view.xml',
        'wizard/raw_material_report_wizard.xml',
    ],
}
