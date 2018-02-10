from odoo import tools
from odoo import fields,models
import openerp.addons.decimal_precision as dp
import time
import logging
from odoo.tools.translate import _
from odoo import api


_logger = logging.getLogger(__name__)
SPP_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class spp(models.Model):
    _name         = 'anggaran.spp'

    @api.depends('spm_ids')
    def _spm_exists(self):
        res = {}
        for spp in self:
            if spp.spm_ids:
                spp.spm_exists = True
        
    name = fields.Char('Nomor', required=True, readonly=True)
    tanggal = fields.Date('Tanggal', required=True)
    period_id = fields.Many2one(comodel_name='anggaran.period', string=_('Perioda'),  required=True)
    tahun_id = fields.Many2one(comodel_name='anggaran.fiscalyear', string='Tahun')
    kepada = fields.Char('Kepada', required=True)
    unit_id = fields.Many2one(comodel_name='anggaran.unit', string=_('Unit'), required=True)
    rka_id = fields.Many2one(comodel_name='anggaran.rka', string=_('Dasar ROA'), required=True)
    #        dasar_rkat = fields.Char('Dasar RKAT Nomor/Tanggal', required=True)
    jumlah = fields.Float('Jumlah Pembayaran', required=True)
    keperluan = fields.Char('Untuk Keperluan', required=True)
    cara_bayar = fields.Selection([('tup','UUDP'),('ls','Pembayaran LS')],'Cara Bayar',required=True)
    alamat = fields.Text('Alamat')
    nomor_rek = fields.Char('Nomor Rekening')
    nama_bank = fields.Char('Nama Bank')

    spp_line_ids = fields.One2many(comodel_name='anggaran.spp_line',inverse_name='spp_id',string='Penjelasan', ondelete="cascade")

    pumkc_id = fields.Many2one(comodel_name='hr.employee', string='PUMKC')
    #nip_pumkc = fields.Related('pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True)
    nip_pumkc = fields.Char(string="nip_pumkc", required=False, )
    
    atasan_pumkc_id = fields.Many2one(comodel_name='hr.employee', string='Atasan Langsung PUMKC')
    #nip_atasan_pumkc = fields.Related('atasan_pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True)
    nip_atasan_pumkc = fields.Char(string="nip_atasan_pumkc", required=False, )
    
    user_id = fields.Many2one(comodel_name='res.users', string='Created', required=True,readonly=True)
    state = fields.Selection(selection=SPP_STATES,string='Status',readonly=True,required=True)

    sptb_id = fields.Many2one(comodel_name='anggaran.sptb', string='SPTB')
    spm_ids = fields.One2many(comodel_name='anggaran.spm',inverse_name='spp_id',string='SPM')
    spm_exists = fields.Boolean(compute="_spm_exists", string='SPM Sudah Tercatat', help="Apakah SPP ini sudah dicatatkan SPM-nya.")

    _defaults = {
        'state'           : SPP_STATES[0][0],
        'tanggal'         : lambda *a : time.strftime("%Y-%m-%d") ,
        'user_id'        : lambda obj, cr, uid, context: uid,
        'name'            : lambda obj, cr, uid, context: '/',        
    }
    def action_draft(self,cr,uid,ids,context=None):
        #set to "draft" state
        return self.write(cr,uid,ids,{'state':SPP_STATES[0][0]},context=context)
    
    def action_confirm(self,cr,uid,ids,context=None):
        #set to "confirmed" state


        return self.write(cr,uid,ids,{'state':SPP_STATES[1][0]},context=context)
    
    def action_reject(self,cr,uid,ids,context=None):
        #set to "done" state
        return self.write(cr,uid,ids,{'state':SPP_STATES[2][0]},context=context)
    
    def action_done(self,cr,uid,ids,context=None):
        #set to "done" state

        #update realisasi di rka_detail.realisasi
        #dari spp -> spp_line -> spp_line_mak.rka_coa_id dengan nilai spp_ini
        for spp in self:
            for spp_line in spp.spp_line_ids:
                for spp_line_mak in spp_line.spp_line_mak_ids:
                    sql = "update anggaran_rka_coa "
                    sql += "set realisasi = coalesce(realisasi,0) + %f " % (spp_line_mak.spp_ini)
                    sql += "where mak_id = %s " % (spp_line_mak.rka_coa_id.mak_id.id)
                    print sql 
                    cr.execute(sql)

        return self.write(cr,uid,ids,{'state':SPP_STATES[3][0]},context=context)

    def create(self, vals):

        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('anggaran.spp') or '/'
        new_id = super(spp, self).create(vals)
        return new_id

    def action_create_spm(self,cr,uid,ids,context=None):
        spp = self.browse(ids[0], context)
        #############################################################
        # cari rka utk unit_id
        #############################################################
        rka_obj = self.env["anggaran.rka"]
        search = [('unit_id.id','=', spp.unit_id.id)]
        rka_ids = rka_obj.search(cr,uid, search)
        for rka in rka_obj.browse(rka_ids):    
            kebijakan_ids = []
            for keg in rka.rka_kegiatan_ids:
                kebijakan_ids += keg.kebijakan_id

            spm_line_ids = [(0,0,{
                    'kebijakan_id' : keg.kebijakan_id.id
                }) for bij 
                in set(kebijakan_ids) ]

        spm_obj = self.env["anggaran.spm"]
        data = {
            'name'             : '/',
            'tanggal'         : time.strftime("%Y-%m-%d") ,
            'cara_bayar'    : 'gup',
            'unit_id'         : spp.unit_id.id,
            'tahun_id'        : spp.tahun_id.id,
            'jumlah'         : spp.jumlah,
            'sisa'             : 0.0,
            'user_id'        : uid, 
            'state'         : 'draft',
            'spp_id'        : spp.id,
            'spm_line_ids'    : spm_line_ids
        }
        spm_id = spm_obj.create(cr,uid,data,context)
        return spm_id

    def action_view_spm(self):
        '''
        This function returns an action that display existing spm 
        of given kas ids. It can either be a in a list or in a form view, 
        if there is only one spm to show.
        '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']

        result = mod_obj.get_object_reference('anggaran', 'action_spm_list')
        id = result and result[1] or False
        result = act_obj.read([id])[0]
        #compute the number of spm to display
        spm_ids = []
        for kas in self:
            spm_ids += [spm.id for spm in kas.spm_ids]
        #choose the view_mode accordingly
        if len(spm_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, spm_ids))+"])]"
        else:
            res = mod_obj.get_object_reference('anggaran', 'view_spm_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = spm_ids and spm_ids[0] or False
        return result

    @api.onchange('spp_line_ids') 
    def on_change_spp_line_ids(self):
        jumlah = 0.0
        for line in self.spp_line_ids:
            jumlah += line.spp_ini 
        self.jumlah = jumlah 

class spp_line(models.Model):
    _name         = "anggaran.spp_line"
    spp_id = fields.Many2one(comodel_name='anggaran.spp', string='SPP')
    rka_kegiatan_id = fields.Many2one(comodel_name='anggaran.rka_kegiatan', string='Kegiatan Bersangkutan')
    pagu = fields.Float('PAGU')
    spp_lalu = fields.Float("SPP sd yg Lalu")
    spp_ini = fields.Float("SPP ini")
    jumlah_spp = fields.Float("Jumlah SPP")
    sisa_dana = fields.Float("Sisa Dana")
    spp_line_mak_ids = fields.One2many(comodel_name='anggaran.spp_line_mak',inverse_name='spp_line_id',string='MAKs', ondelete="cascade")


    @api.onchange('rka_kegiatan_id','spp_ini') 
    def on_change_rka_kegiatan_id(self):
        self.pagu         = self.rka_kegiatan_id.anggaran
        self.spp_lalu     = self.rka_kegiatan_id.realisasi
        self.jumlah_spp = self.spp_lalu + self.spp_ini 
        self.sisa_dana     = self.pagu - self.jumlah_spp

    @api.onchange('spp_line_mak_ids') 
    def on_change_spp_line_mak_ids(self):
        total_spp_ini = 0.0
        for line in self.spp_line_mak_ids:
            total_spp_ini = total_spp_ini + line.spp_ini

        self.spp_ini = total_spp_ini


class spp_line_mak(models.Model):
    _name         = "anggaran.spp_line_mak"

    spp_line_id = fields.Many2one(comodel_name='anggaran.spp_line', string='SPP Line')
    rka_coa_id = fields.Many2one(comodel_name='anggaran.rka_coa', string='MAK')
    pagu = fields.Float('PAGU')
    spp_lalu = fields.Float("SPP sd yg Lalu")
    spp_ini = fields.Float("SPP ini", required=True)
    jumlah_spp = fields.Float("Jumlah SPP")
    sisa_dana = fields.Float("Sisa Dana")


    @api.onchange('rka_coa_id','spp_ini') 
    def on_change_rka_coa_id(self):
        self.pagu         = self.rka_coa_id.total
        self.spp_lalu     = self.rka_coa_id.realisasi
        self.jumlah_spp = self.spp_lalu + self.spp_ini 
        self.sisa_dana     = self.pagu - self.jumlah_spp

