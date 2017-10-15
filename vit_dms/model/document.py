from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
STATE=[('draft','Draft'), ('published','Current'),('archived','Void')]

class document(models.Model):
    _name = 'muk_dms.file'
    _inherit = 'muk_dms.file'

    number              = fields.Char("Number")
    title               = fields.Char("Title")
    document_type_id    = fields.Many2one(comodel_name="dms.document_type", string="Document Type", required=False, )

    date_upload         = fields.Datetime(string="Date Upload", required=False, default=lambda self: time.strftime("%Y-%m-%d %H:%M:%S"))
    date_start          = fields.Date(string="Date Start", required=True, )
    date_end            = fields.Date(string="Date End", required=True, )

    description         = fields.Text(string="Description", required=False, )

    state               = fields.Selection(string="State", selection=STATE, required=True, default=STATE[0][0] )

    @api.model
    def create(self, vals):
        vals['number']    = self.env['ir.sequence'].next_by_code('muk_dms.file')
        return super(document, self).create(vals)

    @api.multi
    def action_draft(self):
        self.state = STATE[0][0]

    @api.multi
    def action_publish(self):
        self.state = STATE[1][0]

    @api.multi
    def action_archive(self):
        self.state = STATE[2][0]
