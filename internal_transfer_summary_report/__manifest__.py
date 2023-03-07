# -*- coding: utf-8 -*-
{
    'name': "internal_transfer_summary_report",

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
    'depends': ['base','report_xlsx'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/reports.xml',
        'wizard/internal_transfer_wizard.xml',
        'views/internal_transfer_report_view.xml',
        'wizard/payment_collection_wizard.xml',
        'views/payment_collection_report_view.xml',
        'wizard/do_print_report.xml',
        'views/do_print_report.xml',
        'wizard/internal_transfer_sum_wizard.xml',
        'views/internal_transfer_sum_report_view.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
