from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class feature(models.Model):
    _name = 'vit_scrum.feature'
    _rec_name = 'name'
    _description = 'Scrum Features'
    _inherit = ['vit_scrum.epic','mail.thread', 'ir.needaction_mixin']

    name            = fields.Char('Name', required=True)
    epic_id         = fields.Many2one(comodel_name="vit_scrum.epic", string="Epic", required=True, )
    backlog_ids     = fields.One2many(comodel_name="vit_scrum.backlog", inverse_name="feature_id", string="Backlogs", required=False, )
