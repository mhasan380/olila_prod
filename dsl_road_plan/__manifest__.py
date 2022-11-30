# -*- coding: utf-8 -*-
{
    'name': "dsl_road_plan",

    'summary': """
        Route Plan developed by Daffodil Computers""",

    'description': """
        Long description of module's purpose is to handle route plan of an user
    """,

    'author': "Firoz, Rafiul",
    'website': "https://daffodil-bd.com",

    # Categories can be used to filter modules in modules listing

    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','olila_sale'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/olila_data.xml',
        'views/day_view.xml',
        'views/territory_view.xml',
        'views/area_view.xml',
        'views/route_master_view.xml',
        'views/zone_view.xml',
        'security/rod_plan_security.xml',
        'views/sales_person.xml',
    ],
}
