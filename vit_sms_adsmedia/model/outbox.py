from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
import simplejson
_logger = logging.getLogger(__name__)

import requests

RESPONSES = {
    10:"Success",
    20:"Json Post Error",
    30:"ApiKey not register",
    40:"Ip address not register",
    35:"Check Balance Limit",
    25:"Error Check Balance",
}

SENDING_STATUS = {
    10: 'Success',
    60: 'Invalid Number',
    70: 'Invalid Message',
    80: 'Minimum Balance',
    90: 'System Error',
}

class outbox(models.Model):
    _name = 'vit_sms.outbox'
    _inherit = 'vit_sms.outbox'

    # actual send SMS via gateway
    def send_gateway(self):
        _logger.info('send_gateway on vit_sms_adsmedia')

        config = self.env['vit_sms.config'].search([('code','=','AdsMedia')])

        if self.config_id == config :
            json_data = {
                "apikey":config.api_key,
                # "senderid":"0",
                # "callbackurl":"",
                "datapacket":
                [
                    {"number":self.destination,"message":self.message}
                ]
            }

            url = config.hostname
            r = requests.post(url, json=json_data)
            _logger.info("response %s %s %s"  % (r.status_code, r.reason, r.text))

            rtext = simplejson.loads(r.text)
            results = rtext['sending_respon'][0]

            # 0 is good, else error
            messageid = int(results['globalstatus']) #status koneksi
            error_message = RESPONSES[messageid]
            if messageid == 10 :
                messageid = int(results['datapacket'][0]['packet']['sendingstatus'])
                error_message = results['datapacket'][0]['packet']['sendingstatustext']
            if messageid == 10 : #status kirim
                status = 0
            else :
                status = messageid
            return (status, error_message, messageid)
        return super(outbox, self).send_gateway()

    @api.model
    def create(self, vals):
        if not vals.get('config_id', False):
            vals['config_id'] = self.env.ref('vit_sms_adsmedia.vit_sms_config_adsmedia').id
        return super(outbox, self).create(vals)
