from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class sprint_burndown(models.Model):
    """
    record how many backlogs done and inprogress for a sprint every day.
    inserted every day by cron on daily basis    
    """
    _name = 'vit_scrum.sprint_burndown'
    _rec_name = 'name'

    sprint_id = fields.Many2one(comodel_name="vit_scrum.sprint", string="Sprint", required=False, )
    date = fields.Date(string="Date", required=False, )

    done_backlog_count = fields.Integer(string="Done Backlogs Count", required=False,)
    open_backlog_count = fields.Integer(string="Open Backlogs Count", required=False,)


    def cron_daily(self, today=False):
        """
        calculate remaining backlogs for today for every sprint
        :return: 
        """
        if not today:
            today = time.strftime("%Y-%m-%d")

        for sprint in self.env['vit_scrum.sprint'].search([('state','=','open')]):
            for backlog in sprint.backlog_ids:
                if backlog.date_actual_end == '':
                    return


