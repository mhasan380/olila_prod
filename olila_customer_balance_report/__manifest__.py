# -*- coding: utf-8 -*-

{
    'name': 'Customer Available Balance Report',
    'version': '1.0',
    'category': 'Sales',
    'summary': 'Customer Available Balance Report',
    'description':'''Customer Available Balance Report''',
    'depends': ['sale'],
    'data': [
        'security/ir.model.access.csv',
        'reports/customer_balance_report_view.xml',
        'wizard/customer_balance_report_wizard_view.xml',


    ],
    'installable': True,
    'application': True,
}