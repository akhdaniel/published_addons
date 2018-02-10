from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class sprint(models.Model):
    _name = 'vit_scrum.sprint'
    _rec_name = 'name'
    _description = 'Scrum Sprints'
    _inherit = ['vit_scrum.release','mail.thread', 'ir.needaction_mixin']

    name = fields.Char('Name', required=True)
    release_id = fields.Many2one(comodel_name="vit_scrum.release", string="Release", required=False, )
    backlog_ids = fields.One2many(comodel_name="vit_scrum.backlog", inverse_name="sprint_id", string="Backlogs", required=False, )

    @api.depends('backlog_ids','state')
    def _compute_done_backlog_count(self):
        count=0
        for sprint in self:
            for back in sprint.backlog_ids:
                if back.state in ['done']:
                    count+=1
            sprint.done_backlog_count = count

    @api.depends('backlog_ids','state')
    def _compute_open_backlog_count(self):
        count=0
        for sprint in self:
            for back in sprint.backlog_ids:
                if back.state in ['draft','open']:
                    count+=1
            sprint.open_backlog_count = count

    done_backlog_count = fields.Integer(string="Done Backlogs Count", required=False, compute='_compute_done_backlog_count', store=True)
    open_backlog_count = fields.Integer(string="Open Backlogs Count", required=False, compute='_compute_open_backlog_count', store=True)


