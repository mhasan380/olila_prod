# -*- coding: utf-8 -*-

{
    'name': 'Purchase Requisition Report',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Print Sale Order Without Price',
    'description':'''Print Sale Order Without Price''',
    'depends': ['purchase_request','purchase'],
    'data': [
        'views/report.xml',
        'views/purchase_request.xml',


    ],
    'installable': True,
    'application': True,
}