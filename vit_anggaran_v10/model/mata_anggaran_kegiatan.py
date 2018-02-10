from odoo import tools
from odoo import api, fields, models
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class mata_anggaran_kegiatan(models.Model):
    _name = "anggaran.mata_anggaran_kegiatan"
    _description = 'mata anggaran kegiatan'

    name = fields.Char(_('Nama'), size=64, required=False, readonly=False)
    code = fields.Char(_('Kode'), size=64, required=False, readonly=False)
    kebijakan_id = fields.Many2one('anggaran.kebijakan', _('Kebijakan'),  required=True,)
    category_id = fields.Many2one(comodel_name="anggaran.category",
                                  string=_("Kategori Kebijakan"),
                                  required=False, related="kebijakan_id.category_id")

    program_id = fields.Many2one('anggaran.program', _('Program'),  required=True,)
    kegiatan_id = fields.Many2one('anggaran.kegiatan', _('Kegiatan'),  required=True,)

    cost_type_id = fields.Many2one('anggaran.cost_type', _('Cost type') ,  required=True,)
    coa_id = fields.Many2one('account.account', _('COA') )


    @api.onchange('kegiatan_id','cost_type_id') # if these fields are changed, call method
    def on_change(self):
        if self.kegiatan_id.code != False and self.cost_type_id != False:
            self.code = '650.1.%s.%s'  % (self.kegiatan_id.code , self.cost_type_id.code  )
            self.name = self.cost_type_id.name 

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


