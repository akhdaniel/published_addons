from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class classification(models.Model):
    _name = 'dms.classification'

    name = fields.Char("Name")
