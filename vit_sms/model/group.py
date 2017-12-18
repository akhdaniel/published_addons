from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class group(models.Model):
    _name = 'vit_sms.group'

    name = fields.Char("Name")
    partner_ids = fields.Many2many(comodel_name="res.partner", string="Partners", )
