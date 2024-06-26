# -*- coding: utf-8 -*-
{
    'name': "customer_details_report",

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
    'depends': ['base'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'report/report_actions.xml',
        'report/customer_outstanding_report.xml',
        'wizard/customer_outstanding.xml',
        'wizard/customer_balance_wizard.xml',
        'report/customer_balance_report_view.xml',
        'wizard/undelivered_sales_order.xml',
        'report/undelivered_sales_order_report_view.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
