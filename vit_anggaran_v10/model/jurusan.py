from odoo import tools
from odoo import api,fields,models
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class jurusan(models.Model):
    _name         = "anggaran.jurusan"
    code        = fields.Char(_('Kode'), required=True)
    name        = fields.Char(_('Nama'), required=True)
    jurusan_id  = fields.Many2one('anggaran.jurusan', _('Jurusan'), required=False)
    fakultas_id = fields.Many2one('anggaran.fakultas', _('Fakultas'), required=True)
    income_ids  = fields.One2many('anggaran.jurusan_income','jurusan_id','Incomes', ondelete="cascade")


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



class jurusan_income(models.Model):
    _name         = "anggaran.jurusan_income"

    @api.depends("jumlah","tarif_spp")
    def _ftotal_spp(self):

        for jur in self:
            jur.total_spp = jur.jumlah * jur.tarif_spp


    @api.depends("jumlah","tarif_spp")
    def _ftotal_bpp(self):
        for jur in self:
            jur.total_bpp = jur.jumlah * jur.tarif_bpp

    @api.depends("total_bpp","total_spp")
    def _ftotal(self):
        for jur in self:
            jur.total = jur.total_spp + jur.total_bpp

    jurusan_id      = fields.Many2one('anggaran.jurusan', 'Jurusan')
    tahun_akademik  = fields.Many2one('anggaran.tahun_akademik', 'Tahun Akademik')
    angkatan        = fields.Many2one('anggaran.tahun_akademik', 'Angkatan')
    jumlah          = fields.Integer('Jumlah Mhs. Aktif')
    tarif_bpp       = fields.Integer('Tarif BPP')
    tarif_spp       = fields.Integer('Tarif SPP')

    total_bpp       = fields.Integer(compute="_ftotal_bpp", string="Total BPP")
    total_spp       = fields.Integer(compute="_ftotal_spp", string="Total SPP")
    total           = fields.Integer(compute="_ftotal", string="Total")


class tahun_akademik(models.Model):
    _name         = "anggaran.tahun_akademik"

    code = fields.Char("Code")
    name = fields.Char("Tahun Akademik")



