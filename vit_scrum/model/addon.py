from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class addon(models.Model):
    _name = 'vit_scrum.addon'
    _rec_name = 'name'
    _description = 'Addon'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Name')
