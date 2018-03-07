from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class config(models.Model):
    _name = 'vit_sms.config'
    _inherit = 'vit_sms.config'

    zenziva_url = fields.Char(string="Zenziva URL", required=False, help="URL for sending plain SMS")
