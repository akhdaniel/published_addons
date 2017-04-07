from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    npwp = fields.Char(string="NPWP", required=False, )
