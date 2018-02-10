from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
SUP_STATES =[ 	('draft','Draft'),
				('open','Verifikasi'), 
				('reject','Ditolak'),
                ('done','Disetujui')]

class sup(osv.osv):
	_name 		= 'anggaran.sup'

	def _spm_exists(self, cursor, user, ids, name, arg, context=None):
		res = {}
		for sup in self.browse(cursor, user, ids, context=context):
			res[sup.id] = False
			if sup.spm_ids:
				res[sup.id] = True
		return res

	_columns 	= {
		'name' 				: fields.char('Nomor' , readonly=True, required=True ),
		'tanggal' 			: fields.date('Tanggal', required=True),
		'tahun_id'		    : fields.many2one('account.fiscalyear', 'Tahun'),
		'period_id'		    : fields.many2one('account.period', 'Period'),
		'lampiran'			: fields.integer('Lampiran'),
		'perihal' 			: fields.char('Perihal', required=True),
		'kepada'  			: fields.text('Kepada', required=True),
		# 'dasar_rkat' 		: fields.char('Dasar RKAT Nomor/Tanggal', required=True),
		'dasar_rkat' 		: fields.many2one('anggaran.rka', 'Dasar ROA', required=True),
		'jumlah'  			: fields.float('Jumlah', required=True),
		'unit_id' 			: fields.many2one('anggaran.unit', 'Atas Nama', required=True),
		'nomor_rek' 		: fields.char('Nomor Rekening'),
		'nama_bank' 		: fields.char('Nama Bank'),

		'pumkc_id'     		: fields.many2one('hr.employee', 'PUMKC'),
		'nip_pumkc' 		: fields.related('pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True),
		'atasan_pumkc_id'   : fields.many2one('hr.employee', 'Atasan Langsung PUMKC'),
		'nip_atasan_pumkc' 	: fields.related('atasan_pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True),

		'state'             : fields.selection(SUP_STATES,'Status',readonly=True,required=True),
		'user_id'	    	: fields.many2one('res.users', 'Created'),
		'spm_ids'			: fields.one2many('anggaran.spm','sup_id','SPM'),
		'spm_exists'		: fields.function(_spm_exists, 
			string='SPM Sudah Tercatat',  
		    type='boolean', help="Apakah UP ni sudah dicatatkan SPM-nya."),		
	}
	_defaults = {
		'state'       	: SUP_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',
		'perihal'		: 'Permohonan Uang Persediaan',
		'kepada'		: 'Bendahara Pusat',
	}

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.sup') or '/'
		new_id = super(sup, self).create(cr, uid, vals, context=context)
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
		sup = self.browse(cr, uid, ids[0], context)

		#############################################################
		# cari rka utk unit_id
		#############################################################
		rka_obj = self.pool.get("anggaran.rka")
		search = [('unit_id.id','=', sup.unit_id.id)]
		rka_ids = rka_obj.search(cr,uid, search, context=context)
		for rka in rka_obj.browse(cr, uid, rka_ids, context=context):	
			kebijakan_ids = []
			for keg in rka.rka_kegiatan_ids:
				kebijakan_ids += keg.kebijakan_id

			spm_line_ids = [(0,0,{
					'kebijakan_id' : keg.kebijakan_id.id
				}) for bij 
				in set(kebijakan_ids) ]

		spm_obj = self.pool.get("anggaran.spm")
		data = {
			'name' 			: '/',
			'tanggal' 		: time.strftime("%Y-%m-%d") ,
			'cara_bayar'    : 'up',
			'unit_id'	 	: sup.unit_id.id,
			'tahun_id'		: sup.tahun_id.id,
			'jumlah' 		: sup.jumlah,
			'sisa' 			: 0.0,
			'user_id'	    : uid, 
			'state'         : 'draft',
			'sup_id'		: sup.id,
			'spm_line_ids'	: spm_line_ids
		}
		spm_id = spm_obj.create(cr,uid,data,context)
		return spm_id

	def action_view_spm(self, cr, uid, ids, context=None):
		'''
		This function returns an action that display existing spm 
		of given kas ids. It can either be a in a list or in a form view, 
		if there is only one spm to show.
		'''
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		result = mod_obj.get_object_reference(cr, uid, 'anggaran', 'action_spm_list')
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		#compute the number of spm to display
		spm_ids = []
		for kas in self.browse(cr, uid, ids, context=context):
			spm_ids += [spm.id for spm in kas.spm_ids]
		#choose the view_mode accordingly
		if len(spm_ids)>1:
			result['domain'] = "[('id','in',["+','.join(map(str, spm_ids))+"])]"
		else:
			res = mod_obj.get_object_reference(cr, uid, 'anggaran', 'view_spm_form')
			result['views'] = [(res and res[1] or False, 'form')]
			result['res_id'] = spm_ids and spm_ids[0] or False
		return result