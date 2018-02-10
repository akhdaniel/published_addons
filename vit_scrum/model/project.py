from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class project(models.Model):
    _name = 'project.project'
    _inherit = 'project.project'

    epic_ids = fields.One2many(comodel_name="vit_scrum.epic", inverse_name="project_id", string="Epics", required=False, )
    release_ids = fields.One2many(comodel_name="vit_scrum.release", inverse_name="project_id", string="Releases", required=False, )

    def _compute_release_count(self):
        for project in self:
            project.release_count = len(project.release_ids)

    release_count  = fields.Integer(string="Release Count", required=False, compute='_compute_release_count')
