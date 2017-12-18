from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
import simplejson
_logger = logging.getLogger(__name__)

import requests


class outbox(models.Model):
    _name = 'vit_sms.outbox'
    _inherit = 'vit_sms.outbox'

    config_id       = fields.Many2one(comodel_name="vit_sms.config", string="Gateway Config", required=False)

    # actual send SMS via gateway
    def send_gateway(self):
        _logger.info('send_gateway on vit_sms_nusasms')

        config = self.env['vit_sms.config'].search([('code','=','NusaSMS')])

        if self.config_id == config:
            data = {'user'      : config.username,
                    'password'  : config.password,
                    'SMSText'   : self.message,
                    'GSM'       : self.destination,
                    'output'    : 'json'
                    }
            r = requests.post(config.hostname, data=data)
            _logger.info("response %s %s %s"  % (r.status_code, r.reason, r.text))

            status = 0
            error_message = ''
            return (status, error_message)


    # set config default to NusaSMS
    @api.model
    def create(self, vals):
        config = self.env['vit_sms.config'].search([('code','=','MySMSMasking')])
        vals['config_id']    = config.id
        return super(outbox, self).create(vals)

