# -*- coding: utf-8 -*-
##############################################################################
# For copyright and license notices, see __openerp__.py file in module root
# directory
##############################################################################
from odoo import models, fields, api
import logging
_logger = logging.getLogger(__name__)


class res_currency(models.Model):
    _inherit = "res.currency"

    inverse_rate = fields.Float(
        'Current Inverse Rate', digits=(12, 4),
        compute='get_inverse_rate',
        help='The rate of the currency from the currency of rate 1 (0 if no '
                'rate defined).'
    )

    @api.one
    @api.depends('rate')
    def get_inverse_rate(self):
        self.inverse_rate = self.rate and (
            1.0 / (self.rate))


    rate = fields.Float(compute='_compute_current_rate', string='Current Rate', digits=(12, 12),
                        help='The rate of the currency to the currency of rate 1.')


    @api.multi
    @api.depends('rate_ids.rate')
    def _compute_current_rate(self):
        date = self._context.get('date') or fields.Datetime.now()
        company_id = self._context.get('company_id') or self.env['res.users']._get_company().id
        # the subquery selects the last rate before 'date' for the given currency/company
        query = """SELECT c.id, (SELECT r.rate FROM res_currency_rate r
                                  WHERE r.currency_id = c.id AND r.name <= %s
                                    AND (r.company_id IS NULL OR r.company_id = %s)
                               ORDER BY r.company_id, r.name DESC
                                  LIMIT 1) AS rate
                   FROM res_currency c
                   WHERE c.id IN %s"""
        self._cr.execute(query, (date, company_id, tuple(self.ids)))
        currency_rates = dict(self._cr.fetchall())
        for currency in self:
            currency.rate = currency_rates.get(currency.id) or 1.0

class res_currency_rate(models.Model):
    _inherit = "res.currency.rate"
    rate = fields.Float(string='Current Rate', digits=(12, 12),)

    inverse_rate = fields.Float(
        'Inverse Rate', digits=(12, 4),
        compute='get_inverse_rate',
        inverse='set_inverse_rate',
        help='The rate of the currency from the currency of rate 1',
    )

    @api.one
    @api.depends('rate')
    def get_inverse_rate(self):
        self.inverse_rate = self.rate and (1.0 / (self.rate))

    @api.one
    def set_inverse_rate(self):
        self.rate = self.inverse_rate and (1.0 / (self.inverse_rate))



