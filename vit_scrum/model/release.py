from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
STATES = [('draft', 'Draft'), ('open', 'In Progress'), ('done', 'Done')]

class release(models.Model):
    _name = 'vit_scrum.release'
    _rec_name = 'name'
    _description = 'Scrum Releases'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name            = fields.Char('Name', required=True)
    description     = fields.Text('Description')

    date_start      = fields.Date(string="Start Date", required=False, )
    date_end        = fields.Date(string="End Date", required=False, )
    duration        = fields.Integer(string="Duration", required=False, help="Days")


    date_start_notes    = fields.Char(string="Start Notes", required=False, help="eg 9 days in progress")
    date_end_notes      = fields.Char(string="End Notes", required=False, help="eg should have ended 2 days ago")

    project_id      = fields.Many2one(comodel_name="project.project", string="Project", required=True, )
    tag_ids         = fields.Many2many(comodel_name="project.tags",  string="Tags", )
    sprint_ids      = fields.One2many(comodel_name="vit_scrum.sprint", inverse_name="release_id", string="Sprints", required=False, )

    state           = fields.Selection(string="State", selection=STATES, required=True, default='draft' )


    @api.multi
    def action_draft(self):
        self.state = STATES[0][0]

    @api.multi
    def action_open(self):
        self.state = STATES[1][0]

    @api.multi
    def action_done(self):
        self.state = STATES[2][0]

