from odoo import tools
from odoo import fields,models
import odoo.addons.decimal_precision as dp
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)
SUP_STATES =[('draft','Draft'),
                ('open','Verifikasi'), 
                ('reject','Ditolak'),
                ('done','Disetujui')]

class sup(models.Model):
    _name = 'anggaran.sup'

    def _spm_exists(self):
        for sup in self:
            sup.spm_exists= False
            if sup.spm_ids:
                sup.spm_exists = True

    name = fields.Char('Nomor' , readonly=True, required=True )
    tanggal = fields.Date('Tanggal', required=True)
    tahun_id = fields.Many2one('anggaran.fiscalyear', 'Tahun')
    period_id = fields.Many2one('anggaran.period', 'Period')
    lampiran = fields.Integer('Lampiran')
    perihal = fields.Char('Perihal', required=True)
    kepada = fields.Text('Kepada', required=True)

    #        dasar_rkat = fields.Char('Dasar RKAT Nomor/Tanggal', required=True)
    dasar_rkat = fields.Many2one('anggaran.rka', 'Dasar ROA', required=True)
    jumlah = fields.Float('Jumlah', required=True)
    unit_id = fields.Many2one('anggaran.unit', 'Atas Nama', required=True)
    nomor_rek = fields.Char('Nomor Rekening')
    nama_bank = fields.Char('Nama Bank')

    pumkc_id = fields.Many2one('hr.employee', 'PUMKC')
    nip_pumkc = fields.Char(
        #related='pumkc_id.otherid',store=True,
        string='NIP PUMKC', readonly=True)

    atasan_pumkc_id = fields.Many2one('hr.employee', 'Atasan Langsung PUMKC')
    nip_atasan_pumkc = fields.Char(
        #related='atasan_pumkc_id.otherid', store=True,
        string='NIP Atasan PUMKC', readonly=True)

    state = fields.Selection(SUP_STATES,'Status',readonly=True,required=True)
    user_id = fields.Many2one('res.users', 'Created')
    #spm_ids = fields.One2many('anggaran.spm','sup_id','SPM')
    #compute="_spm_exists",
    spm_exists = fields.Boolean(string='SPM Sudah Tercatat', help="Apakah UP ni sudah dicatatkan SPM-nya.")

    _defaults = {
        'state' : SUP_STATES[0][0],
        'tanggal' : lambda *a : time.strftime("%Y-%m-%d") ,
        'user_id' : lambda obj, cr, uid, context: uid,
        'name' : lambda obj, cr, uid, context: '/',
        'perihal' : 'Permohonan Uang Persediaan',
        'kepada' : 'Bendahara Pusat',
    }

    def create(self, vals):

        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('anggaran.sup') or '/'
        new_id = super(sup, self).create(vals)
        return new_id
        
    def action_draft(self,cr,uid,ids,context=None):
        #set to "draft" state
        return self.write(cr,uid,ids,{'state':SUP_STATES[0][0]},context=context)
    
    def action_confirm(self,cr,uid,ids,context=None):
        #set to "confirmed" state
        return self.write(cr,uid,ids,{'state':SUP_STATES[1][0]},context=context)
    
    def action_reject(self,cr,uid,ids,context=None):
        #set to "reject" state
        return self.write(cr,uid,ids,{'state':SUP_STATES[2][0]},context=context)    
        
    def action_done(self,cr,uid,ids,context=None):
        #set to "done" state
        return self.write(cr,uid,ids,{'state':SUP_STATES[3][0]},context=context)

    def action_create_spm(self,cr,uid,ids,context=None):
        sup = self.browse(ids[0], context)

        #############################################################
        # cari rka utk unit_id
        #############################################################
        rka_obj = self.env["anggaran.rka"]
        search = [('unit_id.id','=', sup.unit_id.id)]
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
            'cara_bayar'    : 'up',
            'unit_id'         : sup.unit_id.id,
            'tahun_id'        : sup.tahun_id.id,
            'jumlah'         : sup.jumlah,
            'sisa'             : 0.0,
            'user_id'        : uid, 
            'state'         : 'draft',
            'sup_id'        : sup.id,
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