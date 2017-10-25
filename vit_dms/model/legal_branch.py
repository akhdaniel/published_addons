from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class legal_branch(models.Model):
    _name = 'dms.legal_branch'

    name                    = fields.Char("Name")
    region_id               = fields.Many2one(comodel_name="dms.legal_region", string="Region", required=False, )
    legal_status_grade_id   = fields.Many2one(comodel_name="dms.legal_status_grade", string="Status Legal Grade", required=False, )
    legal_status_bisnis_grade_id = fields.Many2one(comodel_name="dms.legal_status_bisnis_grade", string="Status Business Grade", required=False, )
    legal_hasil_penyesuaian_id = fields.Many2one(comodel_name="dms.legal_hasil_penyesuaian", string="Hasil Penyesuaian", help="Hasil Penyesuaian u/ dilaporkan ke OJK",required=False, )
    address                 = fields.Char(string="Alamat Kantor Existing", required=False, )

    #state_id                = fields.Many2one(comodel_name="res.country.state", string="Provinsi", required=False, )
    state_id                = fields.Char(string="Provinsi", required=False, )

    legal_ids = fields.One2many(comodel_name="dms.legal", inverse_name="branch_id", string="Legal Documents", required=False, )

