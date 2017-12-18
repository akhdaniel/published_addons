from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
STATES=[('sent', 'Sent'), ('delivered', 'Delivered'), ('failed','Failed') ]

class sent(models.Model):
    _name = 'vit_sms.sent'
    _inherit = ['vit_sms.outbox']

    state           = fields.Selection(string="State", selection=STATES, required=False, default='sent')
