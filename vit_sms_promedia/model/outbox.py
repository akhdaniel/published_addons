from odoo import api, fields, models, _
import logging
import xml.etree.ElementTree
_logger = logging.getLogger(__name__)

import requests

import dicttoxml


class outbox(models.Model):
    _name = 'vit_sms.outbox'
    _inherit = 'vit_sms.outbox'

    config_id       = fields.Many2one(comodel_name="vit_sms.config", string="Gateway Config", required=False)

    # actual send SMS via gateway
    def send_gateway(self):
        _logger.info('send_gateway on vit_sms_promedia')

        config = self.env['vit_sms.config'].search([('code','=','promedia')])

        if self.config_id == config:
            data = {'username'  : config.username,
                    'password'  : config.password,
                    'priority'  : 'high',
                    'sender'    : 'MMI',
                    # 'dr_url'    : '',
                    'allowduplicate': '0',
                    'data_packet':{
                        'packet':{
                            'msisdn':self.destination,
                            'sms':self.message,
                            'is_long_sms':'N',
                        }
                    }
                }

            xml_data = dicttoxml.dicttoxml(data)
            url = config.hostname + config.promedia_url
            r = requests.post(url, data={'data':xml_data})
            _logger.info("response %s %s %s"  % (r.status_code, r.reason, r.text))

            status, status_text, transation_id = (-1, '', 'empty', '0')

            root = xml.etree.ElementTree.fromstring(r.text)
            for child in root:
                if child.tag=='status_code':
                    status = int(child.text)
                elif child.tag=='status_text':
                    status_text = child.text
                elif child.tag=='transation_id':
                    transation_id = child.text


            return (status, status_text, transation_id)


    # set config default to Promedia
    @api.model
    def create(self, vals):
        config = self.env['vit_sms.config'].search([('code','=','promedia')])
        vals['config_id']    = config.id
        return super(outbox, self).create(vals)

