from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
MOSCOW = [('must', 'Must'), ('should', 'Should'), ('could','Could'), ('wont','Wont'), ('notset','Not Set') ]
KANO = [('exitement', 'Exitement'), ('indifferent', 'Indifferent'), ('mandatory','mandatory'), ('performance','Performance'), ('questionable','Questionable'), ('reverse','Reverse'), ('notset','Not Set') ]

class epic(models.Model):
    _name = 'vit_scrum.epic'
    _rec_name = 'name'
    _description = 'Scrum Features'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    STATES = [('draft', 'Draft'), ('open', 'In Progress'), ('done', 'Done')]

    name                = fields.Char('Name', required=True)
    description         = fields.Text(string="Description", required=False, )

    effort              = fields.Float(string="Effort",  required=False, )
    value               = fields.Float(string="Value",  required=False, )
    risk                = fields.Float(string="Risk",  required=False, )

    moscow              = fields.Selection(string="MoSCow", selection=MOSCOW, required=False, )
    kano                = fields.Selection(string="KANO", selection=KANO, required=False, )

    date_plan_start     = fields.Date(string="Planned Start Date", required=False, default=lambda self: datetime.now().strftime("%Y-%m-%d"))
    date_plan_end       = fields.Date(string="Planned End Date", required=False, default=lambda self:(datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'))
    plan_duration       = fields.Float(string="Planned Duration",  required=False, default=1)

    date_actual_start     = fields.Date(string="Actual Start Date", required=False, )
    date_actual_end       = fields.Date(string="Actual End Date", required=False, )
    actual_duration       = fields.Float(string="Actual Duration",  required=False, )

    feature_ids         = fields.One2many(comodel_name="vit_scrum.feature", inverse_name="epic_id", string="Features", required=False, )
    attachment          = fields.Binary(string="Attachment",  )

    is_ready            = fields.Boolean(string="Is Ready?",  )
    is_waiting          = fields.Boolean(string="Is Waiting?",  )
    is_impended         = fields.Boolean(string="Is Impended?",  )

    project_id          = fields.Many2one(comodel_name="project.project", string="Project", required=True, )
    tag_ids             = fields.Many2many(comodel_name="project.tags",  string="Tags", )
    state               = fields.Selection(string="State", selection=STATES, required=True, default='draft')
