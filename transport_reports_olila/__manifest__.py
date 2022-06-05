# -*- coding: utf-8 -*-
{
    'name': "transport_reports_olila",

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
    'depends': ['olila_fleet'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/vehicle_license_renew.xml',
        'views/templates.xml',
        'views/delivery_details_view.xml',
        'wizard/delivery_details_wizard.xml',
        'wizard/vehicle_paper_wizard.xml',
        'views/vehicle_paper_report_view.xml',
        'wizard/vehicle_paper_cost_wizard.xml',
        'views/vehicle_paper_report_cost_view.xml',
        'wizard/fuel_consumption_details_wizard.xml'
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
