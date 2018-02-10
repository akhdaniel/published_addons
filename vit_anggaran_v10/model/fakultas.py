from odoo import tools
from odoo import api, fields, models
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class fakultas(models.Model):
    _name       = "anggaran.fakultas"
    code        = fields.Char(_('Kode'), required=True)
    name        = fields.Char(_('Nama'), required=True)
    alamat      = fields.Char(_('Alamat'))
    nama_bank   = fields.Char(_('Nama Bank'))
    nomor_rek   = fields.Char(_('No Rekening'))

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


