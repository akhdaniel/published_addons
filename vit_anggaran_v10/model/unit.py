from odoo import tools
from odoo import api, fields, models
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class unit(models.Model):
    _name         = "anggaran.unit"
    code = fields.Char('Kode', required=True, index=True)
    name = fields.Char('Nama', required=True)
    jurusan_id = fields.Many2one('anggaran.jurusan', 'Jurusan')
    fakultas_id = fields.Many2one('anggaran.fakultas', 'Fakultas', related="jurusan_id.fakultas_id", store=True)
    company_id = fields.Many2one('res.company', 'Universitas', required=True)


    @api.onchange('fakultas_id','jurusan_id') # if these fields are changed, call method
    def on_change(self):

        if self.jurusan_id.id != False :
            self.code = '%s'  % (self.jurusan_id.code  )
            self.name = 'Unit Kerja %s' % (self.jurusan_id.name )
        
        elif self.fakultas_id.id != False :
            self.code = '%s'  % (self.fakultas_id.code  )
            self.name = 'Unit Kerja Fakultas %s' % (self.fakultas_id.name )


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


