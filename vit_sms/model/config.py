from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class config(models.Model):
    _name = 'vit_sms.config'

    code     = fields.Char(string="Code", required=False, )
    name     = fields.Char(string="Name", required=False, )
    hostname = fields.Char("Hostname")
    username = fields.Char("Username")
    password = fields.Char("Password")

    priority = fields.Integer(string="Priority", required=False, default=10)
