from odoo import tools
from odoo import api, fields, models
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)
BIAYA_STATES = (('draft', 'Draft'), ('open', 'Verifikasi'), ('reject', 'Ditolak'),
                ('done', 'Disetujui'))


class biaya(models.Model):
    _name = 'anggaran.biaya'

    name = fields.Char('Nomor', required=True, readonly=True)
    tanggal = fields.Date('Tanggal', required=True)
    unit_id = fields.Many2one(comodel_name='anggaran.unit', string='Unit Kerja')
    tahun_id = fields.Many2one(comodel_name='anggaran.fiscalyear', string='Tahun')
    kas_id = fields.Many2one(comodel_name='anggaran.kas', string='Kas Keluar', domain=[('type', '=', 'out')])
    keperluan = fields.Many2one(comodel_name='anggaran.rka_kegiatan', string='Untuk Keperluan')
    total = fields.Float("Total Biaya")
    kepada_partner_id = fields.Many2one(comodel_name='res.partner', string='Dibayarkan Kepada', help="Partner (Supplier/Perorangan) penerima")

    biaya_line_ids = fields.One2many(comodel_name='anggaran.biaya_line', inverse_name='biaya_id', string='Penjelasan', ondelete="cascade"),

    pumkc_id = fields.Many2one(comodel_name='hr.employee',string= 'PUMKC')
    #nip_pumkc = fields.Related('pumkc_id', 'otherid', type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True)
    nip_pumkc = fields.Char(string="nip_pumkc", required=False, )

    atasan_pumkc_id = fields.Many2one(comodel_name='hr.employee', string='Atasan Langsung PUMKC')
    #nip_atasan_pumkc = fields.Related('atasan_pumkc_id', 'otherid', type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True)
    new_field = fields.Char(string="nip_atasan_pumkc", required=False, )

    user_id = fields.Many2one(comodel_name='res.users', string='Created', required=True, readonly=True)
    state = fields.Selection(selection=BIAYA_STATES, string='Status', readonly=True, required=True)

    _defaults = {
        'state'       : BIAYA_STATES[0]
        [0],'tanggal'         : lambda *a : time.strftime(
        "%Y-%m-%d") ,
        'user_id'        : lambda obj, cr, uid,context: uid,
        'name'            : lambda obj, cr,uid, context: '/',
    }

    def action_draft(self,cr,uid, ids,context=None):
        # set to "draft" state
        return self.write(cr, uid, ids, {'state': BIAYA_STATES[0][0]}, context=context)

    def action_confirm (self,cr,uid,ids, context=None):
        # set to "confirmed" state
        return self. write(cr, uid, ids, {'state': BIAYA_STATES[1][0]},context=context)
    
    def action_reject(self,cr,uid,ids,context=None):
        # set to "done" state
        return self. write(cr, uid, ids, {'state': BIAYA_STATES[2][0]}, context=context)

    def action_done( self,cr,uid,ids,context=None):
        # set to "done" state
        return self . write(cr, uid, ids, {'state': BIAYA_STATES[3][0]}, context=context)

    def create(self, vals):
        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('anggaran.biaya') or '/'
        new_id = super(biaya, self).create(vals)
        return new_id

class biaya_line(models.Model):
    _name = "anggaran.biaya_line"
    # def _sudah_sptb_search(self, obj, name, args):
    #     #########################################################
    #     # return list of tuples [('id','in',[1,2,3,4])]
    #     # dimana 1,2,3,4 adalah id record yang mathcing dengan
    #     # yang dicari (misalnya yang sudah di-sptb, mana aja id nya)
    #     #########################################################
    #     data = [('sptb_line_ids','!=',False)]
    #     res = self.search(data)
    #     if not res:
    #         return [('id', '=', 0)]


    #     return [('id', 'in', [x[0] for x in res])]
    def _sudah_sptb(self, name, arg):
        res = {}
        for    biaya_line in self:
            res[biaya_line.id] =False
            if biaya_line.sptb_line_ids:
                res[biaya_line.id] = True
        return res

    biaya_id = fields.Many2one(comodel_name='anggaran.biaya', string='Biaya')
    rka_coa_id = fields.Many2one(comodel_name='anggaran.rka_coa',string='COA Bersangkutan')
    biaya_ini = fields.Float("Jumlah")
    uraian = fields.Char('Uraian')
    sptb_line_ids = fields.One2many(comodel_name='anggaran.sptb_line',inverse_name='biaya_line_id',string='SPTB Item')
    sudah_sptb = fields.Boolean(string='Sudah di-SPTB-kan', help="Apakah biaya ini sudah dicatatkan ke SPTB.")

