from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class legal_status_bisnis_grade(models.Model):
    _name = 'dms.legal_status_bisnis_grade'

    name = fields.Char("Name")
