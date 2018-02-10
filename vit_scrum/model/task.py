from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class task(models.Model):
    _name = 'project.task'
    _inherit = 'project.task'


    backlog_id = fields.Many2one(comodel_name="vit_scrum.backlog", string="Backlog", required=False, )