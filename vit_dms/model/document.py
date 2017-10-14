from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
STATE=[('draft','Draft'), ('published','Published'),('archived','Archived')]

class document(models.Model):
    _name = 'dms.document'
    _rec_name = 'name'
    _description = 'Document'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name                = fields.Char("Name")
    document_type_id    = fields.Many2one(comodel_name="dms.document_type", string="Document Type", required=True, )
    department_id       = fields.Many2one(comodel_name="hr.department", string="Directorate", required=True, )

    date_upload         = fields.Datetime(string="Date Upload", required=False, default=lambda self: time.strftime("%Y-%m-%d %H:%M:%S"))
    date_start          = fields.Date(string="Date Start", required=True, )
    date_end            = fields.Date(string="Date End", required=True, )

    filename            = fields.Binary(string="File Name", required=True )
    filesize            = fields.Integer(string="File Size", required=True )
    state               = fields.Selection(string="State", selection=STATE, required=True, default=STATE[0][0] )

    @api.multi
    def action_draft(self):
        self.state = STATE[0][0]

    @api.multi
    def action_publish(self):
        self.state = STATE[1][0]

    @api.multi
    def action_arcive(self):
        self.state = STATE[2][0]
