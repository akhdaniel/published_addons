from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class legal_region(models.Model):
    _name = 'dms.legal_region'

    name = fields.Char("Name")
