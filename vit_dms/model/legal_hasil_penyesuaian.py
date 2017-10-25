from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class legal_hasil_penyesuaian(models.Model):
    _name = 'dms.legal_hasil_penyesuaian'

    name = fields.Char("Name")
