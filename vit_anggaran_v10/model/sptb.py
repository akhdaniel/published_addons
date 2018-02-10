from odoo import tools
from odoo import fields,models,api
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)
SPTB_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class sptb(models.Model):
    _name         = 'anggaran.sptb'

    @api.depends('spp_ids')
    def _spp_exists(self):
        for sptb in self:
            sptb.spp_exists = False
            if sptb.spp_ids:
                sptb.spp_exists = True


    @api.depends('spp_ids')
    def _total(self):
        res = {}
        for sptb in self:
            if sptb.sptb_line_ids:
                total = 0.0
                for sl in sptb.sptb_line_ids:
                    total += sl.jumlah
                sptb.total = total


    name = fields.Char('Nomor')
    tanggal = fields.Date('Tanggal', readonly=True)
    tahun_id = fields.Many2one(comodel_name='anggaran.fiscalyear', string='Tahun', readonly=True)
    unit_id = fields.Many2one(comodel_name='anggaran.unit', string='Unit Kerja', readonly=True)

    jenis_belanja_id = fields.Many2one(comodel_name='account.account', string= 'Jenis Belanja', required=True)
    rka_kegiatan_id = fields.Many2one(comodel_name='anggaran.rka_kegiatan', string='Kegiatan')
    program_id = fields.Char(string="program_id", required=False, )
    kebijakan_id = fields.Char(string="kebijakan_id", required=False, )
    #program_id = fields.Related('rka_kegiatan_id', 'kegiatan_id' , 'program_id',type="many2one", relation="anggaran.program", string="Program",  readonly=True)
    #kebijakan_id = fields.Related('program_id','kebijakan_id', type="many2one", relation="anggaran.kebijakan", string="Kebijakan",  readonly=True)
    
    sptb_line_ids = fields.One2many(comodel_name='anggaran.sptb_line',inverse_name='sptb_id',string='Penjelasan', ondelete="cascade")

    pumkc = fields.Many2one(comodel_name='hr.employee', string='PUMKC')
    #nip_pumkc = fields.Related('pumkc', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True)
    nip_pumkc = fields.Char(string="nip_pumkc", required=False, )

    kasubag_aftik = fields.Many2one(comodel_name='hr.employee', string='Kasubag AFTIK')
    #nip_kasubag_aftik = fields.Related('kasubag_aftik', 'otherid' , type='char', relation='hr.employee', string='NIP Kasubag AFTIK', store=True, readonly=True)
    nip_kasubag_aftik = fields.Char(string="nip_kasubag_aftik", required=False, )

    atasan_pumkc = fields.Many2one('hr.employee', 'Atasan Langsung PUMKC')
    #nip_atasan_pumkc = fields.Related('atasan_pumkc', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True)
    nip_atasan_pumkc = fields.Char(string="nip_atasan_pumkc", required=False, )

    div_anggaran = fields.Many2one('hr.employee', 'Divisi Anggaran')
    #nip_div_anggaran = fields.Related('div_anggaran', 'otherid' , type='char', relation='hr.employee', string='NIP Divisi Anggaran', store=True, readonly=True)
    nip_div_anggaran = fields.Char(string="nip_div_anggaran", required=False, )

    div_akuntansi = fields.Many2one('hr.employee', 'Divisi Akuntansi')
    #nip_div_akuntansi = fields.Related('div_akuntansi', 'otherid' , type='char', relation='hr.employee', string='NIP Divisi Akuntansi', store=True, readonly=True)
    nip_div_akuntansi = fields.Char(string="nip_div_akuntansi", required=False, )

    user_id = fields.Many2one(comodel_name='res.users', string='Created')
    state = fields.Selection(selection=SPTB_STATES,string='Status',readonly=True,required=True)

    spp_ids = fields.One2many(comodel_name='anggaran.spp',inverse_name='sptb_id', string='SPP')
    spp_exists = fields.Boolean(string='SPP Sudah Tercatat', help="Apakah SPTB ini sudah dicatatkan SPP nya.")
    total = fields.Float(string='Total', ) #compute="_total",

    _defaults = {
        'state'           : SPTB_STATES[0][0],
        'tanggal'         : lambda *a : time.strftime("%Y-%m-%d") ,
        'user_id'        : lambda obj, cr, uid, context: uid,
        'name'            : lambda obj, cr, uid, context: '/',        
    }


    def create(self, vals):

        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('anggaran.sptb') or '/'
        new_id = super(sptb, self).create(vals)
        return new_id

    def action_draft(self,cr,uid,ids,context=None):
        #set to "draft" state
        return self.write(cr,uid,ids,{'state':SPTB_STATES[0][0]},context=context)
    
    def action_confirm(self,cr,uid,ids,context=None):
        #set to "confirmed" state
        return self.write(cr,uid,ids,{'state':SPTB_STATES[1][0]},context=context)
    
    def action_done(self,cr,uid,ids,context=None):
        #set to "done" state
        return self.write(cr,uid,ids,{'state':SPTB_STATES[3][0]},context=context)    

    def action_reject(self,cr,uid,ids,context=None):
        #set to "done" state
        return self.write(cr,uid,ids,{'state':SPTB_STATES[2][0]},context=context)

    def action_tarik_biaya(self,cr,uid,ids,context=None):
        #######################################################################
        # tarik semua biaya_line_id yang blm di SPTB-kan
        # dan COA nya sama dengan jenis_belanja_id
        # dan yang ditujukan kepada partner / bukan unit kerja
        # dan biaya yang sudah done
        # dan milik unit kerja ybs
        #######################################################################
        sptb = self.browse(ids[0])

        bl_obj = self.env["anggaran.biaya_line"]
        search = [
            ('rka_coa_id.coa_id.id','=', sptb.jenis_belanja_id.id),
            ('sptb_line_ids','=',False),
            ('biaya_id.kepada_partner_id','!=', False),
            ('biaya_id.unit_id.id', '=', sptb.unit_id.id),
            ('biaya_id.state','=','done')]
        bl_ids = bl_obj.search(search)

        #######################################################################
        # insert ke sptb_line
        # caranya, update field sptb_line_ids di sptb
        #######################################################################        
        sptb_lines = [(0,0,{
            'penerima_id'   : bl.biaya_id.kas_id.kepada_partner_id.id or False,
            'biaya_line_id' : bl.id,
            'uraian'        : bl.uraian,
            'bukti_no'      : "%s %s" % (bl.biaya_id.kas_id.name,bl.biaya_id.name) ,
            'bukti_tanggal' : bl.biaya_id.kas_id.tanggal,
            'jumlah'         : bl.biaya_ini,
            }) for bl in bl_obj.browse(bl_ids)]

        data = {
            'sptb_line_ids': sptb_lines
        }
        self.write(ids, data)

        return True 


    def action_tarik_sptb(self,cr,uid,ids,context=None):
        #######################################################################
        # cari unit_ids dari unit kerja jurusan di bawah fakultas ini (unit_id)
        # cari sptb milik unit_ids tsb yg sudah done
        # dan belum di-sptb-kan 
        # copy sptb_line ke sptb ini
        #######################################################################        
        sptb = self

        sptb_lines = []
        unit_ids = self.env["anggaran.unit"].search(
            [('jurusan_id.fakultas_id','=',sptb.unit_id.fakultas_id.id)])
        for unit_id in unit_ids:
            sptb_ids = self.search(
                [('unit_id','=', unit_id),('id','<>',sptb.id),
                ('state','=','done')
                ])
            for s_id in sptb_ids:
                sptb_unit = self.browse(s_id)
                for sl in sptb_unit.sptb_line_ids:
                    if sl.sudah_sptb == False: # yang belum di-sptb-kan saja
                        sptb_lines += [(0,0,{
                            'penerima_id'   : sl.penerima_id.id or False,
                            'biaya_line_id' : sl.biaya_line_id.id,
                            'sptb_line_id'  : sl.id,
                            'uraian'        : sl.uraian,
                            'bukti_no'      : sl.bukti_no,
                            'bukti_tanggal' : sl.bukti_tanggal,
                            'jumlah'         : sl.jumlah,
                        }) ]
        data = {
            'sptb_line_ids': sptb_lines
        }
        self.write(ids, data)                
        return True 

    def action_create_spp(self):
        sptb = self
        spp  = self.env["anggaran.spp"]
        data = {
            'name'                 : '/',
            'tanggal'             : time.strftime("%Y-%m-%d"),
            'kepada'              : 'Direktorat Keuangan',
            'dasar_rkat'         : 'MWA/0000',
            'jumlah'              : sptb.total,
            'keperluan'         : '',
            'cara_bayar'          : 'gup',
            'unit_id'              : sptb.unit_id.id,
            'alamat'               : '',
            'nomor_rek'         : '',
            'nama_bank'         : '',
            'spp_line_ids'         : False,
            'user_id'            : self.env.uid,
            'state'               : 'draft',
            'sptb_id'             : sptb.id
        }
        spp_id = spp.create(data)
        return spp_id

    def action_view_spp(self):
        '''
        This function returns an action that display existing spp 
        of given kas ids. It can either be a in a list or in a form view, 
        if there is only one spp to show.
        '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']

        result = mod_obj.get_object_reference('anggaran', 'action_spp_list')
        id = result and result[1] or False
        result = act_obj.read([id])[0]
        #compute the number of spp to display
        spp_ids = []
        for kas in self:
            spp_ids += [spp.id for spp in kas.spp_ids]
        #choose the view_mode accordingly
        if len(spp_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, spp_ids))+"])]"
        else:
            res = mod_obj.get_object_reference('anggaran', 'view_spp_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = spp_ids and spp_ids[0] or False
        return result

class sptb_line(models.Model):
    _name         = "anggaran.sptb_line"

    def _sudah_sptb(self, name, arg):
        res = {}
        for sptb_line in self:
            res[sptb_line.id] = False
            if sptb_line.sptb_line_ids:
                res[sptb_line.id] = True
        return res
    sptb_id = fields.Many2one(comodel_name='anggaran.sptb', string='SPTB')
    penerima_id = fields.Many2one(comodel_name='res.partner', string='Penerima')
    biaya_line_id = fields.Many2one(comodel_name='anggaran.biaya_line', string='Sumber Biaya Item')
    sptb_line_id = fields.Many2one(comodel_name='anggaran.sptb_line', string='Sumber SPTB Item')
    uraian = fields.Char('Uraian')
    bukti_no = fields.Char('No Bukti')
    bukti_tanggal = fields.Char('Tanggal Bukti')
    jumlah = fields.Float("Jumlah")

    sptb_line_ids = fields.One2many(comodel_name='anggaran.sptb_line',inverse_name='sptb_line_id',string='SPTB Items')
    sudah_sptb =  fields.Boolean(
                        string='Sudah di-SPTB-kan',
                        type='boolean',
                        help="Apakah SPTB Jurusan ini sudah dicatatkan ke SPTB lain (Fakultas)."),
    #compute="_sudah_sptb",

