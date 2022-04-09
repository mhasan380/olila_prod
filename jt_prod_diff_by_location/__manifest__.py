# -*- coding: utf-8 -*-
##############################################################################
#
#    Jupical Technologies Pvt. Ltd.
#    Copyright (C) 2018-Today Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>).
#    Author: Jupical Technologies Pvt. Ltd.(<http://www.jupical.com>)
#    you can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name": "Stock Balance Report",
    "version": "14.0.0.1.0",
    "author": "Jupical Technologies Pvt. Ltd.",
    'license': 'AGPL-3',
    "maintainer": "Jupical Technologies Pvt. Ltd.",
    'depends': ['stock'],
    'summary': "Get product stock by warehouse",
    'category': 'stock',
    'live_test_url': 'http://jupical.com/contactus',
    "description": """
    """,
    'data': [
        'security/ir.model.access.csv',
        'views/inventory_report_template.xml',
        'views/report_view.xml',
        'wizard/inventory_report_view.xml',
    ],
    'website': "http://www.jupical.com",
    'installable': True,
    'auto_install': False,
    'images': ['static/description/poster_image.png'],
    'price': 20.00,
    'currency': 'USD',
}
