from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
import simplejson
_logger = logging.getLogger(__name__)

import requests

RESPONSES = {
    0:["Request was successful (all recipients)","ALL_RECIPIENTS_PROCESSED"],
    -1:["Error in processing the request","SEND_ERROR"],
    -2:["Not enough credits on a specific account","NOT_ENOUGH_CREDITS"],
    -3:["Targeted network is not covered on specific account","NETWORK_NOTCOVERED"],
    -5:["Username or password is invalid","INVALID_USER_OR_PASS"],
    -6:["Destination address is missing in the request","MISSING_DESTINATION_ADDRESS"],
    -7:["Balance has expired","BALANCE_EXPIRED"],
    -11:["Number is not recognized by NusaSMS platform","INVALID_DESTINATION_ADDRESS"],
    -12:["Message is missing in the request","MISSING_MESSAGE"],
    -13:["Number is not recognized by NusaSMS platform","INVALID_DESTINATION_ADDRESS"],
    -22:["Incorrect XML format, caused by syntax error","SYNTAX_ERROR"],
    -23:["General error, reasons may vary","ERROR_PROCESSING"],
    -26:["General API error, reasons may vary","COMMUNICATION_ERROR"],
    -27:["Invalid scheduling parametar","INVALID_SENDDATETIME"],
    -28:["Invalid PushURL in the request","INVALID_DELIVERY_REPORT_PUSH_URL"],
    -30:["Invalid APPID in the request","INVALID_CLIENT_APPID"],
    -33:["Duplicated MessageID in the request","DUPLICATE_MESSAGEID"],
    -34:["Sender name is not allowed","SENDER_NOT_ALLOWED"],
    -40:["Client IP Address Not In White List","IP_ADDRESS_FORBIDDEN"],
    -99:["Error in processing request, reasons may vary","GENERAL_ERROR"],
}


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

            url = config.hostname + config.plain_url
            r = requests.post(url, data=data)
            _logger.info("response %s %s %s"  % (r.status_code, r.reason, r.text))

            rtext = simplejson.loads(r.text)
            results = rtext['results'][0]

            # 0 is good, else error
            status = int(results['status'])
            messageid =  results['messageid']
            error_message = RESPONSES[status][0]
            return (status, error_message, messageid)


    # set config default to NusaSMS
    @api.model
    def create(self, vals):
        config = self.env['vit_sms.config'].search([('code','=','NusaSMS')])
        vals['config_id']    = config.id
        return super(outbox, self).create(vals)

