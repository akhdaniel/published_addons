from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class directorate(models.Model):
    _name = 'dms.directorate'
    _rec_name = 'name'
    _description = 'Directorate'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name = fields.Char("Name")
    is_main_menu = fields.Boolean(string="Show in Main Menu", default=True )
