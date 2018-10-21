# -*- coding: utf-8 -*-
##############################################################################
#
#    Copyright (C) 2018 vitraining.com
#    All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    'name': 'Currency Inverse Rate',
    'version': '10.0.0.0.0',
    'category': 'Accounting',
    'sequence': 14,
    'author': 'vitraining.com',
    'website': 'vitraining.com',
    'license': 'AGPL-3',
    'summary': '',
    'description': '''
Currency Inverse Rate
==========================
In some countries where currency rate is big enough compared to USD or EUR, 
we are used to see exchange rate in the inverse way as Odoo shows it. 

The module shows rate FROM base currency and not TO base currency. For eg.

* Base Currency IDR: 1.0
* USD rate: 12,000 (in Odoo way: 1 / 12,000 = 0.000083333333333)

Using this module, we enter the 12,000 and not the 0.000083333333333.

This module also add number of decimal precision on the currency rate
to avoid rounding for those currencies.


Find our other interesting modules that can make your life easier:
https://www.odoo.com/apps/modules/browse?search=vitraining


    ''',
    'depends': [
        'base',
    ],
    'external_dependencies': {
    },
    'data': [
        'views/res_currency_view.xml',
    ],
    'demo': [
    ],
    'test': [
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
}
