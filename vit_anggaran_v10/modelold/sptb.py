from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
SPTB_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class sptb(osv.osv):
	_name 		= 'anggaran.sptb'

	def _spp_exists(self, cursor, user, ids, name, arg, context=None):
		res = {}
		for sptb in self.browse(cursor, user, ids, context=context):
			res[sptb.id] = False
			if sptb.spp_ids:
				res[sptb.id] = True
		return res

	def _total(self, cursor, user, ids, name, arg, context=None):
		res = {}
		for sptb in self.browse(cursor, user, ids, context=context):
			res[sptb.id] = 0.0
			if sptb.sptb_line_ids:
				total = 0.0
				for sl in sptb.sptb_line_ids:
					total += sl.jumlah
				res[sptb.id] = total
		return res

	_columns 	= {
		'name' 				: fields.char('Nomor'),
		'tanggal' 			: fields.date('Tanggal', readonly=True),
		'tahun_id'		   	: fields.many2one('account.fiscalyear', 'Tahun', readonly=True),
		'unit_id'           : fields.many2one('anggaran.unit', 'Unit Kerja', readonly=True),

		'jenis_belanja_id' 	: fields.many2one('account.account', 'Jenis Belanja', required=True),
		'rka_kegiatan_id' 	: fields.many2one('anggaran.rka_kegiatan', 'Kegiatan'),
		'program_id' 		: fields.related('rka_kegiatan_id', 'kegiatan_id' , 'program_id',
								type="many2one", relation="anggaran.program", 
								string="Program",  readonly=True),
		'kebijakan_id'		: fields.related('program_id','kebijakan_id',
								type="many2one", relation="anggaran.kebijakan", 
								string="Kebijakan",  readonly=True),
		'sptb_line_ids'     : fields.one2many('anggaran.sptb_line','sptb_id','Penjelasan', ondelete="cascade"),

		'pumkc'     		: fields.many2one('hr.employee', 'PUMKC'),
		'nip_pumkc' 		: fields.related('pumkc', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True),
		'kasubag_aftik'     : fields.many2one('hr.employee', 'Kasubag AFTIK'),
		'nip_kasubag_aftik' : fields.related('kasubag_aftik', 'otherid' , type='char', relation='hr.employee', string='NIP Kasubag AFTIK', store=True, readonly=True),
		'atasan_pumkc'     	: fields.many2one('hr.employee', 'Atasan Langsung PUMKC'),
		'nip_atasan_pumkc' 	: fields.related('atasan_pumkc', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True),
		'div_anggaran'     	: fields.many2one('hr.employee', 'Divisi Anggaran'),
		'nip_div_anggaran' 	: fields.related('div_anggaran', 'otherid' , type='char', relation='hr.employee', string='NIP Divisi Anggaran', store=True, readonly=True),
		'div_akuntansi'     : fields.many2one('hr.employee', 'Divisi Akuntansi'),
		'nip_div_akuntansi' : fields.related('div_akuntansi', 'otherid' , type='char', relation='hr.employee', string='NIP Divisi Akuntansi', store=True, readonly=True),

		'user_id'	    	: fields.many2one('res.users', 'Created'),
		'state'             : fields.selection(SPTB_STATES,'Status',readonly=True,required=True),

		'spp_ids'			: fields.one2many('anggaran.spp','sptb_id','SPP'),
		'spp_exists'		: fields.function(_spp_exists, 
			string='SPP Sudah Tercatat',  
		    type='boolean', help="Apakah SPTB ini sudah dicatatkan SPP nya."),
		'total'				: fields.function(_total, 
			string='Total', type='float'),
	}
	_defaults = {
		'state'       	: SPTB_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',		
	}


	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.sptb') or '/'
		new_id = super(sptb, self).create(cr, uid, vals, context=context)
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
		sptb = self.browse(cr, uid, ids[0], context=context)

		bl_obj = self.pool.get("anggaran.biaya_line")
		search = [
			('rka_coa_id.coa_id.id','=', sptb.jenis_belanja_id.id),
			('sptb_line_ids','=',False),
			('biaya_id.kepada_partner_id','!=', False),
			('biaya_id.unit_id.id', '=', sptb.unit_id.id),
			('biaya_id.state','=','done')]
		bl_ids = bl_obj.search(cr, uid, search, context=context)

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
			'jumlah' 		: bl.biaya_ini,
			}) for bl in bl_obj.browse(cr, uid, bl_ids, context=context)]

		data = {
			'sptb_line_ids': sptb_lines
		}
		self.write(cr, uid, ids, data, context=context)

		return True 


	def action_tarik_sptb(self,cr,uid,ids,context=None):
		#######################################################################
		# cari unit_ids dari unit kerja jurusan di bawah fakultas ini (unit_id)
		# cari sptb milik unit_ids tsb yg sudah done
		# dan belum di-sptb-kan 
		# copy sptb_line ke sptb ini
		#######################################################################		
		sptb = self.browse(cr, uid, ids, context=context)

		sptb_lines = []
		unit_ids = self.pool.get("anggaran.unit").search(cr, uid, 
			[('jurusan_id.fakultas_id','=',sptb.unit_id.fakultas_id.id)], context=context)
		for unit_id in unit_ids:
			sptb_ids = self.search(cr,uid, 
				[('unit_id','=', unit_id),('id','<>',sptb.id),
				('state','=','done')
				], context=context)
			for s_id in sptb_ids:
				sptb_unit = self.browse(cr, uid, s_id, context=context)
				for sl in sptb_unit.sptb_line_ids:
					if sl.sudah_sptb == False: # yang belum di-sptb-kan saja
						sptb_lines += [(0,0,{
							'penerima_id'   : sl.penerima_id.id or False,
							'biaya_line_id' : sl.biaya_line_id.id,
							'sptb_line_id'  : sl.id,
							'uraian'        : sl.uraian,
							'bukti_no'      : sl.bukti_no,
							'bukti_tanggal' : sl.bukti_tanggal,
							'jumlah' 		: sl.jumlah,
						}) ]
		data = {
			'sptb_line_ids': sptb_lines
		}
		self.write(cr, uid, ids, data, context=context)				
		return True 

	def action_create_spp(self, cr, uid, ids, context=None):
		sptb = self.browse(cr, uid, ids[0], context=context)
		spp  = self.pool.get("anggaran.spp")
		data = {
			'name' 				: '/',
			'tanggal' 			: time.strftime("%Y-%m-%d"),
			'kepada'  			: 'Direktorat Keuangan',
			'dasar_rkat' 		: 'MWA/0000',
			'jumlah'  			: sptb.total,
			'keperluan' 		: '',
			'cara_bayar'      	: 'gup',
			'unit_id'  			: sptb.unit_id.id,
			'alamat'   			: '',
			'nomor_rek' 		: '',
			'nama_bank' 		: '',
			'spp_line_ids' 		: False,
			'user_id'	    	: uid,
			'state'           	: 'draft',
			'sptb_id'     		: sptb.id
		}
		spp_id = spp.create(cr, uid, data, context=context)
		return spp_id

	def action_view_spp(self, cr, uid, ids, context=None):
		'''
		This function returns an action that display existing spp 
		of given kas ids. It can either be a in a list or in a form view, 
		if there is only one spp to show.
		'''
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		result = mod_obj.get_object_reference(cr, uid, 'anggaran', 'action_spp_list')
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		#compute the number of spp to display
		spp_ids = []
		for kas in self.browse(cr, uid, ids, context=context):
			spp_ids += [spp.id for spp in kas.spp_ids]
		#choose the view_mode accordingly
		if len(spp_ids)>1:
			result['domain'] = "[('id','in',["+','.join(map(str, spp_ids))+"])]"
		else:
			res = mod_obj.get_object_reference(cr, uid, 'anggaran', 'view_spp_form')
			result['views'] = [(res and res[1] or False, 'form')]
			result['res_id'] = spp_ids and spp_ids[0] or False
		return result

class sptb_line(osv.osv):
	_name 		= "anggaran.sptb_line"

	def _sudah_sptb(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for sptb_line in self.browse(cr, uid, ids, context=context):
			res[sptb_line.id] = False
			if sptb_line.sptb_line_ids:
				res[sptb_line.id] = True
		return res

	_columns 	= {
		'sptb_id' 		: fields.many2one('anggaran.sptb', 'SPTB'),
		'penerima_id'   : fields.many2one('res.partner', 'Penerima'),
		'biaya_line_id' : fields.many2one('anggaran.biaya_line', 'Sumber Biaya Item'),
		'sptb_line_id'  : fields.many2one('anggaran.sptb_line', 'Sumber SPTB Item'),
		'uraian'        : fields.char('Uraian'),
		'bukti_no'      : fields.char('No Bukti'),
		'bukti_tanggal' : fields.char('Tanggal Bukti'),
		'jumlah' 		: fields.float("Jumlah"),

		'sptb_line_ids'	: fields.one2many('anggaran.sptb_line','sptb_line_id','SPTB Items'),
		'sudah_sptb'	: fields.function(_sudah_sptb, 
							string='Sudah di-SPTB-kan',  
						    type='boolean', 
						    help="Apakah SPTB Jurusan ini sudah dicatatkan ke SPTB lain (Fakultas)."),
	}
