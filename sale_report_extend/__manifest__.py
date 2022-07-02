# -*- coding: utf-8 -*-
{
    'name': "sale_report_extend",

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
    'depends': ['olila_reports'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/sale_summary_report.xml',
        'views/sale_status_report.xml',
        'views/sales_summary_report_view.xml',
        'views/undelivery_value_report.xml',
        'wizard/sales_summary_wizard.xml',
        'wizard/undelivery_stock_report_wizard_view.xml',

    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
