# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import datetime, timedelta
import logging

class accounting_invoice_cron_cancel(models.Model):
    _inherit = "account.invoice"

    @api.multi
    def invoice_autocancel(self, *args):
        days = 10

        def read_days_from_conf():
            return self.env['account.config.settings']\
                .sudo()\
                .get_days_for_cancel()

        days = read_days_from_conf()
        critical_date = datetime.now() - timedelta(days=days)
        partnerIds = map(lambda x: x.id,
                        self.env['res.partner']\
                         .sudo()\
                         .search([('category_id.name','=','Agent')]))
        invoices = list(self\
                        .sudo()\
                        .search([('state','=','open'),
                                ('date_invoice','<',critical_date),
                                ('partner_id','in',partnerIds),
                                ]))

        invQty = len(map(lambda rec: rec.action_invoice_cancel(), invoices))

        listOfOrigins = [inv.origin for inv in invoices]
        saleOrigins = list(self.env['sale.order']\
                    .sudo()\
                    .search([
                        ('name','in',listOfOrigins),
                     ]))

        # also checks whether sales records non empty -
        # i.present in base and have an id
        if len(saleOrigins) == 0:
            saleQty=0
            logging.warning(
                """Cron invoice autocancellation - related sale orders was not found 
                    """)
        else:
            saleQty = len(map(lambda rec: rec.action_cancel(),
                list(set(saleOrigins))))

        logging.info(
            """Cron invoice autocancellation - Success. 
               {0} invoices and {1} sale orders cencelled"""\
                .format(invQty,saleQty))
        return True

    class AccountConfigSettings(models.TransientModel):
        _inherit = "account.config.settings"

        def get_days_for_cancel(self):
            valuesObj = self.env['ir.values']
            value = valuesObj\
                .sudo()\
                .search([('name',"=","numberOfDaysForCancel")],
                        limit=1)
            days = filter(lambda s: s.isdigit(), str(value.value_unpickle)) \
                if value.value_unpickle and len(value.value_unpickle) > 0 \
                else ''
            return 10 if not days else int(days)

        numberOfDaysForCancel = fields.Integer("Number of days to cancel", help="Number of days to cancel \
        opened invoice with related sale order", default=get_days_for_cancel,
                                               defailt_model="account.invoice")

        @api.multi
        def set_account_config_settings(self):
            daysQty = 10

            if isinstance(self.numberOfDaysForCancel,(float,int)):
                daysQty = int(round(self.numberOfDaysForCancel))
                logging.info(
                    "Cron invoice autocancellation - got value: {0}"\
                        .format(str(daysQty)))
            else:
                logging.warning("""Cron invoice autocancellation: 
                                "Warning Wrong Value""")
            self.env["ir.values"].sudo() \
                .set_default("account.invoice",
                             "numberOfDaysForCancel",
                             daysQty,
                             company_id=self.company_id.id)
            return True