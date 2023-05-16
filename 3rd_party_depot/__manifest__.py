# -*- coding: utf-8 -*-
{
    'name': "3rd_party_depot",

    'summary': """
        Short (1 phrase/line) summary of the module's purpose, used as
        subtitle on modules listing or apps.openerp.com""",

    'description': """
        Long description of module's purpose
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock_olila'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/warehouse_security.xml',
        'views/stock_balance_report_view.xml',
        'views/views.xml',
        'views/templates.xml',
        'wizard/stock_balance_report_wizard_view.xml',
        'views/res_config_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
