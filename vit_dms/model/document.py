from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
STATE=[('draft','Draft'), ('published','Current'),('archived','Void')]

class document(models.Model):
    _name = 'muk_dms.file'
    _inherit = 'muk_dms.file'

    def _get_default_classification(self):
        return self.env.ref('vit_dms.class_1', raise_if_not_found=False)

    number              = fields.Char("Number")
    title               = fields.Char("Title")
    document_type_id    = fields.Many2one(comodel_name="dms.document_type", string="Document Type", required=True, )
    classification_id   = fields.Many2one(comodel_name="dms.classification", string="Classification", required=True, default=_get_default_classification)

    date_upload         = fields.Datetime(string="Date Upload", required=False, default=lambda self: time.strftime("%Y-%m-%d %H:%M:%S"))
    date_start          = fields.Date(string="Date Start", required=True, )
    date_end            = fields.Date(string="Date End", required=True, )
    date_published      = fields.Date(string="Date Published", required=True, )
    date_archived       = fields.Date(string="Date Archived", required=True, )

    uploader_id         = fields.Many2one(comodel_name="res.users", string="Uploader", required=False, )

    description         = fields.Text(string="Description", required=False, )
    state               = fields.Selection(string="State", selection=STATE, required=True, default=STATE[0][0] )

    contributor_ids     = fields.One2many(comodel_name="dms.contributor", inverse_name="file_id", string="Contributors", required=False, )

    reff_id             = fields.Many2one(comodel_name="dms.file", string="Reffernce", required=False, )
    related_ids         = fields.Many2many(comodel_name="dms.file", string="Related Documents", )

    @api.model
    def create(self, vals):
        vals['number']    = self.env['ir.sequence'].next_by_code('muk_dms.file')
        return super(document, self).create(vals)

    @api.multi
    def action_draft(self):
        self.state = STATE[0][0]
        self.date_published = False

    @api.multi
    def action_publish(self):
        self.state = STATE[1][0]
        self.date_published = time.strftime("%Y-%m-%d")

    @api.multi
    def action_archive(self):
        self.state = STATE[2][0]
        self.date_archived = time.strftime("%Y-%m-%d")


class contributor(models.Model):
    _name = 'dms.contributor'
    _rec_name = 'partner_id'

    file_id         = fields.Many2one(comodel_name="muk_dms.file", string="Document", required=False, )
    partner_id      = fields.Many2one(comodel_name="res.partner", string="Name", required=False, )
    role            = fields.Char(string="Role", required=False, )