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
    'name': 'DSL Employee Access',
    'version': '14.0.8.0.0',
    'summary': """DSL Employee Access""",
    'description': 'This module enables employee based salesforce management',
    'category': 'hr',
    'author': 'Md. Rafiul Hassan',
    'company': 'DSL',
    'website': "https://daffodil.computer",
    'depends': ['base', 'hr', 'dsl_road_plan', 'sale'],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/employee_res.xml',
        'views/sale_order_other_tab.xml',
        'views/setting_logger_menu.xml',
        # 'views/product_category.xml',
        'views/res_partner.xml'

    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
