from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
SPM_STATES =[('draft','Draft'),('open','Verifikasi'), 
				('reject','Ditolak'),
                 ('done','Disetujui')]

class spm(osv.osv):
	_name 		= "anggaran.spm"

	def _kas_exists(self, cursor, user, ids, name, arg, context=None):
		res = {}
		for spm in self.browse(cursor, user, ids, context=context):
			res[spm.id] = False
			if spm.kas_ids:
				res[spm.id] = True
		return res	


	_columns 	= {
		'name' 				: fields.char("Nomor", readonly=True),
		'tanggal' 			: fields.date("Tanggal"),
		'cara_bayar'        : fields.selection([('up','UP'),('gup','GUP'),('tup','TUP'),('ls','LS')],
								'Cara Bayar',required=True),
		'unit_id'	 		: fields.many2one('anggaran.unit', 'Atas Nama'),
		'tahun_id'		    : fields.many2one('account.fiscalyear', 'Tahun'),

		'sup_id'		    : fields.many2one('anggaran.sup', 'UP Asal'),
		'tup_id'		    : fields.many2one('anggaran.tup', 'TUP Asal'),
		'spp_id'		    : fields.many2one('anggaran.spp', 'SPP Asal'),

		'pengguna_id'  		: fields.many2one('hr.employee', 'Pengguna Dana'),
		'nip_pengguna' 		: fields.related('pengguna_id', 'otherid' , type='char', relation='hr.employee', string='NIP Pengguna Dana', store=True, readonly=True),
		'dirkeu_id'    		: fields.many2one('hr.employee', 'Direktur Keuangan'),
		'nip_dirkeu' 		: fields.related('dirkeu_id', 'otherid' , type='char', relation='hr.employee', string='NIP Direktur Keuangan', store=True, readonly=True),	

		'spm_line_ids'		: fields.one2many('anggaran.spm_line','spm_id','Rincian', ondelete="cascade"),
		'jumlah' 			: fields.float('Jumlah SPM'),
		'sisa' 				: fields.float('Sisa Anggaran'),

		'user_id'	    	: fields.many2one('res.users', 'Created'),
		'state'             : fields.selection(SPM_STATES,'Status',readonly=True,required=True),
		'kas_ids'			: fields.one2many('anggaran.kas','spm_id','Kas Keluar'),
		'kas_exists'		: fields.function(_kas_exists, 
			string='Kas Keluar Sudah Tercatat',  
		    type='boolean', help="Apakah SPM ini sudah dicatatkan bukti kas keluar nya."),
	}
	_defaults = {
		'state'       	: SPM_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',
	}

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.spm') or '/'
		new_id = super(spm, self).create(cr, uid, vals, context=context)
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
		spm = self.browse(cr, uid, ids[0], context)

		#################################################################
		# kas object
		#################################################################
		kas_obj = self.pool.get("anggaran.kas")
		
		#################################################################
		# cari unit pusat 
		#################################################################
		unit_pusat_ids =  self.pool.get("anggaran.unit").search(cr, uid, [("code","=","PUSAT")], context=context)
		if not unit_pusat_ids:
			raise osv.except_osv(_('Error'),_("Unit Pusat tidak ditemukan") ) 

		context.update({
			'tahun_id' 			: spm.tahun_id.id, 
			'kegiatan_id' 		: spm.name, 
			'jumlah' 			: spm.jumlah, 
			'unit_id' 			: unit_pusat_ids[0], 
			'contra_unit' 		: spm.unit_id.id, 
			'kegiatan_id' 		: False,
			'dasar_pembayaran' 	: '',
			'jenis_item'  		: 'um',
			'sumber_uang' 		: spm.cara_bayar,
			'spm_id' 			: spm.id,

		})
		kas_id = kas_obj.create_kas(cr, uid, 'out', context )
		
		return kas_id

	def action_view_kas(self, cr, uid, ids, context=None):
		'''
		This function returns an action that display existing kas 
		of given kas ids. It can either be a in a list or in a form view, 
		if there is only one kas to show.
		'''
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		result = mod_obj.get_object_reference(cr, uid, 'anggaran', 'action_kas_keluar_list')
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		#compute the number of kas to display
		kas_ids = []
		for kas in self.browse(cr, uid, ids, context=context):
			kas_ids += [kas.id for kas in kas.kas_ids]
		#choose the view_mode accordingly
		if len(kas_ids)>1:
			result['domain'] = "[('id','in',["+','.join(map(str, kas_ids))+"])]"
		else:
			res = mod_obj.get_object_reference(cr, uid, 'anggaran', 'view_kas_form')
			result['views'] = [(res and res[1] or False, 'form')]
			result['res_id'] = kas_ids and kas_ids[0] or False
		return result

class spm_line(osv.osv):
	_name 		= "anggaran.spm_line"
	_columns 	= {
		'spm_id'			: fields.many2one('anggaran.spm', 'SPM'),
		'kebijakan_id' 		: fields.many2one('anggaran.kebijakan', 'Kebijakan'),
		'pagu'				: fields.float('PAGU'),
		'up_sd_lalu'		: fields.float('UP/GUP sd yg Lalu'),
		'up_ini'			: fields.float('UP/GUP Ini'),
		'jumlah_up'			: fields.float('Jumlah sd UP/GUP Ini'),
		'sisa_dana'			: fields.float('Sisa Dana'),
	}