from odoo import tools
from odoo import api, fields, models
import time
import logging
from odoo.tools.translate import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
RKA_STATES =[('draft','Draft'),('open','Verifikasi'),
                 ('done','Disahkan')]

###########################################################################
#Level 1 : RKA
###########################################################################
class rka(models.Model):
    _name         = "anggaran.rka"
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _rec_name   = "period_id"

    @api.onchange('rka_kegiatan_ids') 
    def on_change_rka_kegiatan_ids(self):
        total = 0.0
        for keg in self.rka_kegiatan_ids:
            total = total + keg.anggaran
        print total 
        self.anggaran = total     
    
    def hitung_realisasi(self, array_coas):
        realisasi = 0 
        for ar in array_coas:
            realisasi = realisasi + ar['realisasi']
        return realisasi     

    def hitung_anggaran(self, array_coas):
        realisasi = 0 
        for ar in array_coas:
            realisasi = realisasi + ar['anggaran']
        return realisasi 

    @api.depends("rka_kegiatan_ids","rka_kegiatan_ids2","rka_kegiatan_ids3","rka_kegiatan_ids4")
    def _frealisasi(self):
        for rka in self:
            rka.sisa = self.hitung_realisasi(rka.rka_kegiatan_ids)

    @api.depends("rka_kegiatan_ids","rka_kegiatan_ids2","rka_kegiatan_ids3","rka_kegiatan_ids4")
    def _fsisa(self):
        for rka in self:
            rka.sisa = rka.anggaran - rka.realisasi


    unit_id         = fields.Many2one('anggaran.unit', _('Unit Kerja'), required=True)
    fakultas_id     = fields.Many2one(comodel_name="anggaran.fakultas", string="Fakultas", required=False, related="unit_id.fakultas_id", store=True, readonly=True)
    tahun             = fields.Many2one('anggaran.fiscalyear', _('Tahun'), required=True)
    period_id         = fields.Many2one('anggaran.period', _('Periode') , required=True)

    alokasi         = fields.Float(_('Alokasi'))
    anggaran         = fields.Float('Total Anggaran')
    realisasi         = fields.Float(compute="_frealisasi", string="Realisasi")
    sisa             = fields.Float(compute="_fsisa", string="Sisa")
    definitif         = fields.Float("Definitif")

    rka_kegiatan_ids = fields.One2many('anggaran.rka_kegiatan','rka_id', _('Pendidikan'), ondelete="cascade", domain=[('category_id','ilike','PENDIDIKAN')])
    rka_kegiatan_ids2 = fields.One2many('anggaran.rka_kegiatan','rka_id', _('Pemasaran'), ondelete="cascade", domain=[('category_id','ilike','PEMASARAN')])
    rka_kegiatan_ids3 = fields.One2many('anggaran.rka_kegiatan','rka_id', _('Investasi'), ondelete="cascade", domain=[('category_id','ilike','INVESTASI')])
    rka_kegiatan_ids4 = fields.One2many('anggaran.rka_kegiatan','rka_id', _('Overhead'), ondelete="cascade", domain=[('category_id','ilike','OVERHEAD')])

    state         = fields.Selection(RKA_STATES,'Status',readonly=True,required=True, default=RKA_STATES[0][0])
    note         = fields.Text(_('Note'))
    mak_terisi     = fields.Boolean('MAK Terisi', default=False)

    def action_draft(self):
        #set to "draft" state
        return self.write({'state':RKA_STATES[0][0]})
    
    def action_confirm(self):
        #set to "confirmed" state
        rka = self

        #apakah ada rka dengna perioda yang sama utk tahun ini
        rkas = self.search([('tahun','=',rka.tahun.id ),
            ('period_id','=', rka.period_id.id),
            ('unit_id','=',rka.unit_id.id)])
        if len(rkas) > 1:
            raise UserError(_('Error'),_("Ada lebih dari satu RKA pada perioda yang sama") ) 

        if rka.alokasi < rka.anggaran:
            raise UserError(_('Error'),_("Total Anggaran Melebihi Alokasi") ) 

        if rka.alokasi == 0.0 or rka.anggaran == 0.0:
            raise UserError(_('Error'),_("Mohon dilengkapi data Alokasi dan Total Anggaran") ) 

        return self.write({'state':RKA_STATES[1][0]})
    
    def action_done(self):
        #set to "done" state
        return self.write({'state':RKA_STATES[2][0]})


    ######################################################################
    # looping Kebijakan, Program, Kegiatan, MAK
    # isi ke RKA, RKA Kegiatan, dst, sd rka_coa
    ######################################################################
    def action_fill_mak(self):

        rka = self

        kbj_obj    = self.env['anggaran.kebijakan']
        prg_obj    = self.env['anggaran.program']
        keg_obj    = self.env['anggaran.kegiatan']
        mak_obj    = self.env['anggaran.mata_anggaran_kegiatan']
        rka_keg_obj    = self.env['anggaran.rka_kegiatan']

        rka_kegiatan_ids    = []

        for keg in keg_obj.search([]):

            rka_coa_ids = []


            for mak in mak_obj.search([('kegiatan_id','=', keg.id)]):
                rka_coa_ids.append( (0,0, {
                    'mak_id'            : mak.id,
                    'code'              : mak.code + '.' + self.unit_id.code
                }) )

            #kalau sudah ada record rka_kegiatan_ids utk kegiatan ini, tidak usah diinsert

            exist = rka_keg_obj.search([('rka_id','=', rka.id),('kegiatan_id','=',keg.id)])
            if not exist:
                rka_kegiatan_ids.append( (0,0,{ 
                    'kebijakan_id'         : keg.kebijakan_id.id,
                    'program_id'         : keg.program_id.id,
                    'kegiatan_id'         : keg.id,
                    'indikator'         : '',
                    'target_capaian'     : 0.0,
                    'target_capaian_uom': False,
                    'anggaran'             : 0.0,
                    'rka_coa_ids'        : rka_coa_ids
                }) )
        
        data = {
            'alokasi'            : 0.0,
            'anggaran'            : 0.0,
            'realisasi'            : 0.0,
            'sisa'                 : 0.0, 
            'definitif'            : 0.0,
            'rka_kegiatan_ids'  : rka_kegiatan_ids,
            'state'                 : RKA_STATES[0][0],
            'note'                 : '',
            'mak_terisi'         : True
        }
        self.write( data )
        return 

    def copy(self, default=None):
        default = dict(default or {})
        old = self.browse(id)

        rka_kegiatan_ids = []

        for fd in old.rka_kegiatan_ids:

            rka_coa_ids = []
            for rc in fd.rka_coa_ids:

                rka_detail_ids = []
                for rd in rc.rka_detail_ids:
                    rka_volume_ids = []
                    for rv in rd.rka_volume_ids:
                        rka_volume_ids.append((0,0,{
                            # 'rka_detail_id'  : rv.rka_detail_id,
                            'volume'          : rv.volume,
                            'volume_uom'     : rv.volume_uom.id
                        }))
                    rka_detail_ids.append( (0,0,{
                        # 'rka_coa_id'     : rd.rka_coa_id,
                        'keterangan'    : rd.keterangan,
                        'tarif'             : rd.tarif,
                        'jumlah'        : rd.jumlah,
                        'volume_total'     : rd.volume_total,
                        'rka_volume_ids': rka_volume_ids
                    }))

                rka_coa_ids.append( (0,0, {
                    # 'rka_kegiatan_id'     : rc.rka_kegiatan_id.id,
                    'mak_id'            : rc.mak_id.id,
                    'total'                 : rc.total,
                    'sumber_dana_id'    : rc.sumber_dana_id.id,
                    'bulan'                : rc.bulan,
                    'rka_detail_ids'    : rka_detail_ids

                }) )

            rka_kegiatan_ids.append( (0,0,{ 
                'kebijakan_id'         : fd.kebijakan_id.id,
                'program_id'         : fd.program_id.id,
                'kegiatan_id'         : fd.kegiatan_id.id,
                'indikator'         : fd.indikator,
                'target_capaian'     : fd.target_capaian,
                'target_capaian_uom': fd.target_capaian_uom.id or False,
                'anggaran'             : fd.anggaran,
                'rka_coa_ids'        : rka_coa_ids
            }) )
        
        default.update({'rka_kegiatan_ids' : rka_kegiatan_ids })
        return super(rka, self).copy(id, default)

###########################################################################
#Level 2 : RKA Kegiatan
###########################################################################
class rka_kegiatan(models.Model):
    @api.onchange('rka_coa_ids') 
    def on_change_rka_coa_ids(self):
        total = 0.0
        for coa in self.rka_coa_ids:
            total = total + coa.total
        print total 
        self.anggaran = total 

    
    def hitung_realisasi(self, array_coas):
        realisasi = 0 
        for ar in array_coas:
            realisasi = realisasi + ar['realisasi']
        return realisasi 


    @api.depends("rka_coa_ids")
    def _frealisasi(self):
        for rka in self:
            rka.sisa = self.hitung_realisasi(rka.rka_coa_ids)


    @api.depends("rka_coa_ids")
    def _fsisa(self):
        for rka in self:
            rka.sisa = rka.anggaran - rka.realisasi


    _name             = "anggaran.rka_kegiatan"
    _rec_name       = "kegiatan_id"

    rka_id          = fields.Many2one('anggaran.rka', 'RKA')
    kebijakan_id    = fields.Many2one('anggaran.kebijakan', _('Kebijakan'))
    category_id     = fields.Many2one(comodel_name="anggaran.category",
                                   string=_("Kategori Kebijakan"),
                                   related="kebijakan_id.category_id",
                                   store=True, readonly=True )
    program_id      = fields.Many2one('anggaran.program', _('Program'))
    kegiatan_id     = fields.Many2one('anggaran.kegiatan', _('Kegiatan'))

    unit_id         = fields.Many2one(comodel_name="anggaran.unit", string="Unit", required=False,
                                     related="rka_id.unit_id", readonly=True)

    indikator         = fields.Text(_('Indikator'))
    target_capaian    = fields.Float(_('Target Capaian'))
    target_capaian_uom = fields.Many2one('product.uom', _('Satuan Target'))

    anggaran = fields.Float("Total Anggaran")
    realisasi = fields.Float(compute="_frealisasi", string="Realisasi")
    sisa = fields.Float(compute="_fsisa", string="Sisa")
    definitif = fields.Float("Definitif")

    rka_coa_ids = fields.One2many('anggaran.rka_coa','rka_kegiatan_id', _('Rincian'), ondelete="cascade")



###########################################################################
#Level 3 : RKA Rincian MAK
###########################################################################
class rka_coa(models.Model):
    _rec_name   = "mak_id"
    _name         = "anggaran.rka_coa"

    @api.onchange('rka_detail_ids') 
    def on_change_rka_detail_ids(self):
        total = 0.0
        for det in self.rka_detail_ids:
            total = total + det.volume_total
        print total 
        self.total = total 

    def actual_hitung_jumlah(self, array_detail):
        total = 0 
        for ar in array_detail:
            total = total + ar['volume_total']
        return total 


    @api.multi
    def _frealisasi(self):
        results = {}
        rka_coas = self

        for rka_coa in rka_coas:
            results[rka_coa.id] = 0.0

            for rka_detail in rka_coa.rka_detail_ids:
                if rka_detail.realisasi > 0:
                    results[rka_coa.id] += rka_detail.realisasi

        return results

    def _fsisa(self):
        results = {}
        rka_coas = self

        # ambil satu-per-satu sesion object 
        for rka_coa in rka_coas:
            if rka_coa.total > 0:
                results[rka_coa.id] = rka_coa.total - rka_coa.realisasi
            else:
                results[rka_coa.id] = 0.0

        return results

    def hitung_total(self, array_detail ):
        total = self.actual_hitung_jumlah(array_detail) 
        return total  

    """
    def calculate_total(self, rka_detail_ids):
        array_detail = self.resolve_o2m_commands_to_record_dicts(
            cr, uid, 'rka_detail_ids', rka_detail_ids, ['volume_total']
        )
        results = {
            'value' : {
                'total' : self.hitung_total(array_detail),
                # 'sisa' : self.hitung_sisa(array_detail),
            }
        }
        return results
    """

    rka_kegiatan_id = fields.Many2one('anggaran.rka_kegiatan', 'Kegiatan')
    mak_id = fields.Many2one('anggaran.mata_anggaran_kegiatan', 'MAK')
    code          = fields.Char('Kode')
    total = fields.Float('Total')

    #diupdate waktu SPP confirm
    realisasi = fields.Float('Realisasi')
    sisa = fields.Float(compute="_fsisa", string="Sisa")

    definitif = fields.Float('Definitif Biaya')
    sumber_dana_id = fields.Many2one('anggaran.sumber_dana', 'Sumber Dana')
    bulan = fields.Many2one('anggaran.period', 'Bulan')
    rka_detail_ids = fields.One2many('anggaran.rka_detail','rka_coa_id','Detail', ondelete="cascade")



###########################################################################
#Level 4: detail MAK
###########################################################################
class rka_detail(models.Model):
    _rec_name   = "keterangan"
    _name         = "anggaran.rka_detail"

    @api.onchange('rka_volume_ids','tarif') 
    def on_change_rka_volume_ids(self):
        total = 1
        for vol in self.rka_volume_ids:
            total = total * vol.volume
        self.jumlah = total     
        self.volume_total = total * self.tarif    



    def _fsisa(self, field, arg):
        results = {}
        rka_details = self

        # ambil satu-per-satu sesion object 
        for rka_detail in rka_details:
            if rka_detail.volume_total > 0:
                results[rka_detail.id] = rka_detail.volume_total - rka_detail.realisasi
            else:
                results[rka_detail.id] = 0.0

        return results

    # cari total spp detail MAK ini...
    def hitung_realisasi(self, rka_detail ):
        return 99.0

    @api.multi
    def _frealisasi(self):
        results = {}
        rka_details = self 

        # ambil satu-per-satu rka_detail object 
        for rka_detail in rka_details:
            if rka_detail.volume_total > 0:
                results[rka_detail.id] = self.hitung_realisasi(rka_detail )
            else:
                results[rka_detail.id] = 0.0

        return results

    kebijakan_id = fields.Many2one(comodel_name="anggaran.kebijakan", string="Kebijakan", required=False,
                                   related="rka_coa_id.rka_kegiatan_id.kegiatan_id.program_id.kebijakan_id",
                                   readonly=True,
                                   store=True)
    program_id = fields.Many2one(comodel_name="anggaran.program", string="Program", required=False,
                                 related="rka_coa_id.rka_kegiatan_id.kegiatan_id.program_id",
                                 readonly=True,
                                 store=True)
    kegiatan_id = fields.Many2one(comodel_name="anggaran.kegiatan",
                                  string="Kegiatan",
                                  readonly=True,
                                  related="rka_coa_id.rka_kegiatan_id.kegiatan_id",
                                  store=True)
    unit_id = fields.Many2one(comodel_name="anggaran.unit",
                              string="Unit",
                              readonly=True,
                              related="rka_coa_id.rka_kegiatan_id.unit_id",
                              store=True)

    tahun = fields.Many2one(comodel_name="anggaran.fiscalyear",
                            string="Tahun",
                            readonly=True,
                            related="rka_coa_id.rka_kegiatan_id.rka_id.tahun",
                            store=True)

    period_id = fields.Many2one(comodel_name="anggaran.period", string="Period",
                                readonly=True,
                                related="rka_coa_id.rka_kegiatan_id.rka_id.period_id",
                                store=True)

    rka_coa_id 		= fields.Many2one('anggaran.rka_coa', _('MAK'))
    keterangan 		= fields.Text(_('Keterangan'), required=True)
    tarif 			= fields.Float(_('Tarif'), required=True)
    jumlah 			= fields.Float(_('Jumlah'), required=True)

    volume_total 	= fields.Float(_('Volume Total') , required=True)
    realisasi 		= fields.Float('Realisasi')
    sisa 			= fields.Float('Sisa')
    definitif 		= fields.Float('Definitif Biaya')

    rka_volume_ids = fields.One2many('anggaran.rka_volume','rka_detail_id',_('Volumes'), ondelete="cascade")


    def hitung_jumlah(self, array_volumes):
        jumlah = 1.0 
        for ar in array_volumes:
            jumlah = jumlah * ar['volume']
        return jumlah 

    def hitung_volume_total(self, array_volumes, tarif):
        jumlah = self.hitung_jumlah(array_volumes) 
        return jumlah * tarif



###########################################################################
#Level 5: detail volumes
###########################################################################
class rka_volume(models.Model):
    _name         	= "anggaran.rka_volume"
    rka_detail_id 	= fields.Many2one('anggaran.rka_detail', 'RKA Detail')
    volume 			= fields.Float('Volume')
    volume_uom 		= fields.Many2one('product.uom', 'Satuan Volume')


class fiscalyear(models.Model):
    _name = 'anggaran.fiscalyear'
    name = fields.Char("Year")
    period_ids = fields.One2many(comodel_name="anggaran.period", inverse_name="fiscalyear_id", string="Periods", required=False, )

class period(models.Model):
    _name = 'anggaran.period'
    fiscalyear_id = fields.Many2one(comodel_name="anggaran.fiscalyear", string="Year", required=False, )
    name = fields.Char("Period")
