# -*- coding: utf-8 -*-
###################################################################################
#
#    Daffodil Computers Ltd.
#    Copyright (C) 2022.
#
#    This program is not a free software.
#
###################################################################################
{
    'name': 'DSL Secondary Sales',
    'version': '14.0.1.0.0',
    'summary': """A DSL product for Olila Glassware to manage secondary sales""",
    'description': 'This module enables secondary sale features',
    'category': 'sale',
    'author': 'Md. Rafiul Hassan',
    'company': 'DSL',
    'website': "https://daffodil.computer",
    'depends': ['base', 'hr', 'olila_sale', 'sale', 'web_domain_field', 'stock', 'dsl_employee_access'],
    'data': ['security/access_security.xml',
             'security/ir.model.access.csv',
             'data/secondary_sale_seq.xml',
             'data/primary_customer_stock_seq.xml',
             'data/secondary_customer_seq.xml',
             'views/app_js_templates.xml',
             'views/sales_secondary.xml',
             'views/secondary_sale_order.xml',
             'views/primary_customer_stocks.xml',
             'views/routes.xml',
             'views/sales_secondary_customer.xml',
             'views/secondary_stock_moves.xml'
             ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
