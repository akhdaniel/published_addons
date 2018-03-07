from odoo import api, fields, models, _
import logging
import xml.etree.ElementTree
_logger = logging.getLogger(__name__)

import requests



class outbox(models.Model):
    _name = 'vit_sms.outbox'
    _inherit = 'vit_sms.outbox'

    config_id       = fields.Many2one(comodel_name="vit_sms.config", string="Gateway Config", required=False)

    # actual send SMS via gateway
    def send_gateway(self):
        _logger.info('send_gateway on vit_sms_zenziva')

        config = self.env['vit_sms.config'].search([('code','=','zenziva')])

        if self.config_id == config:
            data = {'userkey'      : config.username,
                    'passkey'  : config.password,
                    'pesan'   : self.message,
                    'nohp'       : self.destination,
                    }

            url = config.hostname + config.zenziva_url
            r = requests.post(url, data=data)
            _logger.info("response %s %s %s"  % (r.status_code, r.reason, r.text))

            status, text, messageid, balance = (-1,'empty','empty', -1)

            root = xml.etree.ElementTree.fromstring(r.text)
            for message in root.find('message'):
                if message.tag=='status':
                    status = message.text
                elif message.tag=='text':
                    text = message.text
                elif message.tag=='to':
                    to = message.text
                elif message.tag=='balance':
                    balance = message.text

            messageid = 'none'
            return (status, text, messageid)


    # set config default to Zenziva
    @api.model
    def create(self, vals):
        config = self.env['vit_sms.config'].search([('code','=','zenziva')])
        vals['config_id']    = config.id
        return super(outbox, self).create(vals)

