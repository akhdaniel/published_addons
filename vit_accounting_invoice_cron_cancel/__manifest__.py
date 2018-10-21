# -*- coding: utf-8 -*-
{
    'name': "Cancel Invoices by Cron",

    'summary': """
        Create a cron job to auto cancel unpaid invoices for certain days""",

    'description': """Create a cron job that runs every day at 00.00 (cron parameter) to check invoices that:
        * belong to a partner with category "Agent"
        * in state of "Open"
        * date invoice is more than x days from now (x is taken from system parameter "invoice.autocancel")

        For every invoices found, execute the existing "Cancel invoice" function (assumed that the sales jurnal is set to "allow cancel").

        Also, cancel all related Sale Order for those Invoices.
        
        
        Find our other interesting modules that can make your life easier:
https://www.odoo.com/apps/modules/browse?search=vitraining

    """,
    'images': ['static/description/images/women-accountants.jpg'],

    'author': "Roman S. Shcherbakov, Akhmad D. Sembiring",
    'website': "http://vitraining.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'sale', 'account'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'data/cronTask.xml'
    ],
}
