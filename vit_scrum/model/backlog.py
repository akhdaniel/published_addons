from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class backlog(models.Model):
    _name = 'vit_scrum.backlog'
    _rec_name = 'name'
    _description = 'Scrum Backlogs'
    _inherit = ['vit_scrum.epic', 'mail.thread', 'ir.needaction_mixin']

    name            = fields.Char('Name')
    description     = fields.Text(string="Description", required=False, )
    acceptance_criteria = fields.Text(string="Acceptance Criteria", required=False, )
    date_due        = fields.Date(string="Due Date", required=False, )


    epic_id         = fields.Many2one(comodel_name="vit_scrum.epic", string="Epic", required=False, )
    feature_id      = fields.Many2one(comodel_name="vit_scrum.feature", string="Feature", required=False, )
    release_id      = fields.Many2one(comodel_name="vit_scrum.release", string="Release", required=False, )
    sprint_id       = fields.Many2one(comodel_name="vit_scrum.sprint", string="Sprint", required=False, )
    addon_id        = fields.Many2one(comodel_name="vit_scrum.addon", string="Addon", required=False, )
    task_ids        = fields.One2many(comodel_name="project.task", inverse_name="backlog_id", string="Tasks", required=False, )

    @api.multi
    def action_draft(self):
        self.state = self.STATES[0][0] # STATES dari epic

    @api.multi
    def action_open(self):
        self.state = self.STATES[1][0]

    @api.multi
    def action_done(self):
        self.state = self.STATES[2][0]

    def write(self, vals):
        if 'sprint_id' in vals:
            vals['release_id'] = self.env['vit_scrum.sprint'].browse(int(vals['sprint_id'])).release_id.id
        return super(backlog, self).write(vals)
