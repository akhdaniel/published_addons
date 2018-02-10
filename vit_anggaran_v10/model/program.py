from odoo import tools
from odoo import api, fields, models
import openerp.addons.decimal_precision as dp
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class program(models.Model):
    """
    Level 2 MAK
    """
    _name         = "anggaran.program"
    name = fields.Text('Nama')
    code = fields.Char('Kode')
    kebijakan_id = fields.Many2one('anggaran.kebijakan', 'Kebijakan', required=True)
    category_id = fields.Many2one(comodel_name="anggaran.category",
                                  string=_("Kategori Kebijakan"),
                                  required=False,
                                  related="kebijakan_id.category_id",
                                  store=True)
    kegiatan_ids = fields.One2many('anggaran.kegiatan','program_id','Kegiatan', ondelete="cascade")


    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + ' ' + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(['|',('name', '=', name),('code', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()


