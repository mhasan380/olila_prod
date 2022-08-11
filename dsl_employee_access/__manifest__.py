# -*- coding: utf-8 -*-
###################################################################################
#    A part of Open HRMS Project <https://www.openhrms.com>
#
#    Daffodil Computers Ltd.
#    Copyright (C) 2020-TODAY Cybrosys Technologies (<https://www.cybrosys.com>).
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
###################################################################################
{
    'name': 'DSL Employee Access',
    'version': '14.0.1.0.0',
    'summary': """DSL Employee Access""",
    'description': 'This module enables invoice auto fill features',
    'category': 'hr',
    'author': 'Md. Rafiul Hassan',
    'company': 'DSL',
    'website': "https://daffodil.computer",
    'depends': ['base', 'hr', 'dsl_road_plan'],
    'data': [
        'security/access_security.xml',
        'security/ir.model.access.csv',
        'views/employee_res.xml',
        'views/setting_logger_menu.xml'

    ],
    'images': ['static/description/banner.png'],
    'license': 'AGPL-3',
    'installable': True,
    'auto_install': False,
    'application': False,
}
