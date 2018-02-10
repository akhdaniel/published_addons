from odoo import tools
from odoo import fields,models,api
import time
import logging
from odoo.tools.translate import _
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)
SPM_STATES =[('draft','Draft'),('open','Verifikasi'), 
                ('reject','Ditolak'),
                 ('done','Disetujui')]

class spm(models.Model):
    _name         = "anggaran.spm"

    @api.depends("kas_ids")
    def _kas_exists(self):
        for spm in self:
            spm.kas_exists = False
            if spm.kas_ids:
                spm.kas_exists = True

    name = fields.Char("Nomor", readonly=True)
    tanggal = fields.Date("Tanggal")
    cara_bayar = fields.Selection([('up','UP'),('gup','GUP'),('tup','TUP'),('ls','LS')], 'Cara Bayar',required=True)
    unit_id = fields.Many2one('anggaran.unit', 'Atas Nama')
    tahun_id = fields.Many2one('anggaran.fiscalyear', 'Tahun')

    sup_id = fields.Many2one('anggaran.sup', 'UP Asal')
    tup_id = fields.Many2one('anggaran.tup', 'TUP Asal')
    spp_id = fields.Many2one('anggaran.spp', 'SPP Asal')

    pengguna_id = fields.Many2one('hr.employee', 'Pengguna Dana')
    nip_pengguna = fields.Char(string='NIP Pengguna Dana', readonly=True,
                               #store=True,
                               )
    dirkeu_id = fields.Many2one('hr.employee', 'Direktur Keuangan')
    nip_dirkeu= fields.Char(string='NIP Direktur Keuangan',
                               #store=True, readonly=True
                             )

    spm_line_ids = fields.One2many(comodel_name='anggaran.spm_line',inverse_name='spm_id',string='Rincian', ondelete="cascade")
    jumlah = fields.Float('Jumlah SPM')
    sisa = fields.Float('Sisa Anggaran')

    user_id = fields.Many2one('res.users', 'Created')
    state = fields.Selection(SPM_STATES,'Status',readonly=True,required=True)
    kas_ids = fields.One2many(comodel_name='anggaran.kas', inverse_name='spm_id',string='Kas Keluar')
    kas_exists = fields.Boolean(compute="_kas_exists", string='Kas Keluar Sudah Tercatat', help="Apakah SPM ini sudah dicatatkan bukti kas keluar nya.")

    _defaults = {
        'state'            : SPM_STATES[0][0],
        'tanggal'         : lambda *a : time.strftime("%Y-%m-%d") ,
        'user_id'        : lambda obj, cr, uid, context: uid,
        'name'            : lambda obj, cr, uid, context: '/',
    }

    def create(self, vals):

        if vals.get('name', '/') == '/':
            vals['name'] = self.env['ir.sequence'].get('anggaran.spm') or '/'
        new_id = super(spm, self).create(vals)
        return new_id
        
    def action_draft(self,cr,uid,ids,context=None):
        #set to "draft" state
        return self.write(cr,uid,ids,{'state':SPM_STATES[0][0]},context=context)
    
    def action_confirm(self,cr,uid,ids,context=None):
        #set to "confirmed" state
        return self.write(cr,uid,ids,{'state':SPM_STATES[1][0]},context=context)

    def action_reject(self,cr,uid,ids,context=None):
        #set to "done" state
        return self.write(cr,uid,ids,{'state':SPM_STATES[2][0]},context=context)
    
    def action_done(self,cr,uid,ids,context=None):
        #set to "done" state
        return self.write(cr,uid,ids,{'state':SPM_STATES[3][0]},context=context)
    
    def action_create_kas_keluar(self,cr,uid,ids,context=None):
        #################################################################
        # spm
        #################################################################
        spm = self.browse(ids[0], context)

        #################################################################
        # kas object
        #################################################################
        kas_obj = self.env["anggaran.kas"]
        
        #################################################################
        # cari unit pusat 
        #################################################################
        unit_pusat_ids =  self.env["anggaran.unit"].search([("code","=","PUSAT")])
        if not unit_pusat_ids:
            raise UserError(_('Error'),_("Unit Pusat tidak ditemukan") ) 

        context.update({
            'tahun_id'             : spm.tahun_id.id, 
            'kegiatan_id'         : spm.name, 
            'jumlah'             : spm.jumlah, 
            'unit_id'             : unit_pusat_ids[0], 
            'contra_unit'         : spm.unit_id.id, 
            'kegiatan_id'         : False,
            'dasar_pembayaran'     : '',
            'jenis_item'          : 'um',
            'sumber_uang'         : spm.cara_bayar,
            'spm_id'             : spm.id,

        })
        kas_id = kas_obj.create_kas('out', context )
        
        return kas_id

    def action_view_kas(self):
        '''
        This function returns an action that display existing kas 
        of given kas ids. It can either be a in a list or in a form view, 
        if there is only one kas to show.
        '''
        mod_obj = self.env['ir.model.data']
        act_obj = self.env['ir.actions.act_window']

        result = mod_obj.get_object_reference('anggaran', 'action_kas_keluar_list')
        id = result and result[1] or False
        result = act_obj.read([id])[0]
        #compute the number of kas to display
        kas_ids = []
        for kas in self:
            kas_ids += [kas.id for kas in kas.kas_ids]
        #choose the view_mode accordingly
        if len(kas_ids)>1:
            result['domain'] = "[('id','in',["+','.join(map(str, kas_ids))+"])]"
        else:
            res = mod_obj.get_object_reference('anggaran', 'view_kas_form')
            result['views'] = [(res and res[1] or False, 'form')]
            result['res_id'] = kas_ids and kas_ids[0] or False
        return result

class spm_line(models.Model):
    _name         = "anggaran.spm_line"

    spm_id = fields.Many2one(string='SPM', comodel_name='anggaran.spm')
    kebijakan_id = fields.Many2one(comodel_name='anggaran.kebijakan', string='Kebijakan')

    pagu = fields.Float('PAGU')
    up_sd_lalu = fields.Float('UP/GUP sd yg Lalu')
    up_ini = fields.Float('UP/GUP Ini')
    jumlah_up = fields.Float('Jumlah sd UP/GUP Ini')
    sisa_dana = fields.Float('Sisa Dana')
