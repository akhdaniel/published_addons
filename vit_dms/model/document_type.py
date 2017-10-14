from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class document_type(models.Model):
    _name = 'dms.document_type'
    _rec_name = 'name'
    _description = 'Document Type'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char("Name")
