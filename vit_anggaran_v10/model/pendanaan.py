from odoo import tools
from odoo import fields,models
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)
PENDANAAN_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class pendanaan(models.Model):
    _name         = 'anggaran.pendanaan'
    name = fields.Char('Nomor', required=True, readonly=True)
    tanggal = fields.Date('Tanggal', required=True)
    unit_id = fields.Many2one('anggaran.unit', 'Unit Kerja')
    tahun_id = fields.Many2one('anggaran.fiscalyear', 'Tahun')
    period_id = fields.Many2one('anggaran.period', 'Period')
    keperluan = fields.Many2one('anggaran.rka_kegiatan', 'Untuk Keperluan')
    total = fields.Float("Total Pendanaan")

    pendanaan_line_ids = fields.One2many('anggaran.pendanaan_line','pendanaan_id','Penjelasan', ondelete="cascade")

    pumkc_id = fields.Many2one('hr.employee', 'PUMKC')
    nip_pumkc = fields.Related('pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True)
    atasan_pumkc_id = fields.Many2one('hr.employee', 'Atasan Langsung PUMKC')
    nip_atasan_pumkc = fields.Related('atasan_pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True)

    user_id = fields.Many2one('res.users', 'Created', required=True,readonly=True)
    state = fields.Selection(PENDANAAN_STATES,'Status',readonly=True,required=True)

    _defaults = {
        'state'           : PENDANAAN_STATES[0][0],
        'tanggal'         : lambda *a : time.strftime("%Y-%m-%d") ,
        'user_id'        : lambda obj, cr, uid, context: uid,
        'name'            : lambda obj, cr, uid, context: '/',        
    }
    def action_draft(self,cr,uid,ids,context=None):
        #set to "draft" state
        return self.write(cr,uid,ids,{'state':PENDANAAN_STATES[0][0]},context=context)
    
    def action_confirm(self,cr,uid,ids,context=None):
        #set to "confirmed" state
        return self.write(cr,uid,ids,{'state':PENDANAAN_STATES[1][0]},context=context)
    
    def action_reject(self,cr,uid,ids,context=None):
        #set to "done" state
        return self.write(cr,uid,ids,{'state':PENDANAAN_STATES[2][0]},context=context)
    
    def action_done(self,cr,uid,ids,context=None):
        #set to "done" state
        return self.write(cr,uid,ids,{'state':PENDANAAN_STATES[3][0]},context=context)

    def create(self, vals):

        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('anggaran.pendanaan') or '/'
        new_id = super(pendanaan, self).create(vals)
        return new_id



class pendanaan_line(models.Model):
    _name         = "anggaran.pendanaan_line"
    pendanaan_id = fields.Many2one('anggaran.pendanaan', 'Pendanaan')
    pendanaan_ini = fields.Float("Jumlah")
    uraian = fields.Char('Uraian')

    sudah_sptb = fields.Boolean(compute="_sudah_sptb",
                        string='Sudah di-SPTB-kan',
                        type='boolean',
                        #fnct_search=_sudah_sptb_search,
                        help="Apakah pendanaan ini sudah dicatatkan ke SPTB."),

