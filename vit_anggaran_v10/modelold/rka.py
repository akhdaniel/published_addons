from openerp import tools
from openerp.osv import fields,osv
from openerp import api
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
RKA_STATES =[('draft','Draft'),('open','Verifikasi'),
				 ('done','Disahkan')]

###########################################################################
#Level 1 : RKA
###########################################################################
class rka(osv.osv):
	_name 		= "anggaran.rka"
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

	def _frealisasi(self, cr, uid, ids, field, arg, context=None):
		results = {}
		rkas = self.browse(cr, uid, ids, context=context) 
		for rka in rkas:
			rka_kegiatan_ids = rka.rka_kegiatan_ids
			results[rka.id] = self.hitung_realisasi(rka_kegiatan_ids)
		return results

	def _fanggaran(self, cr, uid, ids, field, arg, context=None):
		results = {}
		rkas = self.browse(cr, uid, ids, context=context) 
		for rka in rkas:
			rka_kegiatan_ids = rka.rka_kegiatan_ids
			results[rka.id] = self.hitung_anggaran(rka_kegiatan_ids)
		return results

	def _fsisa(self, cr, uid, ids, field, arg, context=None):
		results = {}
		rkas = self.browse(cr, uid, ids, context=context) 
		for rka in rkas:
			results[rka.id] = rka.anggaran - rka.realisasi
		return results


	_columns 	= {
		unit_id = fields.many2one('anggaran.unit', _('Unit Kerja'), required=True)
		fakultas_id = fields.related('unit_id', 'fakultas_id' , type="many2one", relation="anggaran.fakultas", string="Fakultas", store=True)
		tahun = fields.many2one('account.fiscalyear', _('Tahun'), required=True)
		period_id = fields.many2one('account.period', _('Periode') , required=True)
		
		alokasi = fields.float(_('Alokasi'))
		#		anggaran = fields.function(_fanggaran, type='float', string="Total Anggaran")
		anggaran = fields.float('Total Anggaran')
		realisasi = fields.function(_frealisasi, type='float', string="Realisasi")
		sisa = fields.function(_fsisa, type='float', string="Sisa")
		definitif = fields.float("Definitif")

		'rka_kegiatan_ids'  : fields.one2many('anggaran.rka_kegiatan','rka_id', 
								_('Pendidikan'), ondelete="cascade", domain=[('category_id','ilike','PENDIDIKAN')]),

		'rka_kegiatan_ids2'  : fields.one2many('anggaran.rka_kegiatan','rka_id', 
								_('Pemasaran'), ondelete="cascade", domain=[('category_id','ilike','PEMASARAN')]),

		'rka_kegiatan_ids3'  : fields.one2many('anggaran.rka_kegiatan','rka_id', 
								_('Investasi'), ondelete="cascade", domain=[('category_id','ilike','INVESTASI')]),

		'rka_kegiatan_ids4'  : fields.one2many('anggaran.rka_kegiatan','rka_id', 
								_('Overhead'), ondelete="cascade", domain=[('category_id','ilike','OVERHEAD')]),

		state = fields.selection(RKA_STATES,'Status',readonly=True,required=True)
		'note'		 		: fields.text(_('Note')),	
		'mak_terisi'		: fields.boolean('MAK Terisi')	
	}
	
	_defaults = {
		'state'	   : RKA_STATES[0][0],
		'mak_terisi': False 
	}

	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':RKA_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		rka = self.browse(cr, uid, ids[0], context=context)

		#apakah ada rka dengna perioda yang sama utk tahun ini
		rkas = self.search(cr, uid, [('tahun','=',rka.tahun.id ),
			('period_id','=', rka.period_id.id),
			('unit_id','=',rka.unit_id.id)], context=context)
		if len(rkas) > 1:
			raise osv.except_osv(_('Error'),_("Ada lebih dari satu RKA pada perioda yang sama") ) 

		if rka.alokasi < rka.anggaran:
			raise osv.except_osv(_('Error'),_("Total Anggaran Melebihi Alokasi") ) 

		if rka.alokasi == 0.0 or rka.anggaran == 0.0:
			raise osv.except_osv(_('Error'),_("Mohon dilengkapi data Alokasi dan Total Anggaran") ) 

		return self.write(cr,uid,ids,{'state':RKA_STATES[1][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':RKA_STATES[2][0]},context=context)


	######################################################################
	# looping Kebijakan, Program, Kegiatan, MAK
	# isi ke RKA, RKA Kegiatan, dst, sd rka_coa
	######################################################################
	def action_fill_mak(self,cr,uid,ids,context=None):

		rka = self.browse(cr, uid, ids[0], context=context)

		kbj_obj	= self.pool.get('anggaran.kebijakan')
		prg_obj	= self.pool.get('anggaran.program')
		keg_obj	= self.pool.get('anggaran.kegiatan')
		mak_obj	= self.pool.get('anggaran.mata_anggaran_kegiatan')
		rka_keg_obj	= self.pool.get('anggaran.rka_kegiatan')

		rka_kegiatan_ids	= []

		# kbj_ids = kbj_obj.search(cr, uid, [], context=context):
		# for kbj in kbj_obj.browse(cr, uid, kbj_ids, context=context):
		# 	prg_ids = kbj.program_ids
		# 	for prg in prg_obj.browse(cr, uid, prg_ids, context=context):
		# 		keg_ids = prg.kebijakan_ids
		
		keg_ids = keg_obj.search(cr, uid, [], context=context)
		for keg in keg_obj.browse(cr, uid, keg_ids, context=context):

			rka_coa_ids = []

			mak_ids = mak_obj.search(cr, uid, [('kegiatan_id','=', keg.id),('unit_id','=', rka.unit_id.id)], context=context)
			for mak in mak_obj.browse(cr, uid, mak_ids, context=context):
				rka_coa_ids.append( (0,0, {
					'mak_id'			: mak.id,
				}) )

			#kalau sudah ada record rka_kegiatan_ids utk kegiatan ini, tidak usah diinsert

			exist = rka_keg_obj.search(cr, uid, [('rka_id','=', rka.id),('kegiatan_id','=',keg.id)], context=context)
			if not exist:
				rka_kegiatan_ids.append( (0,0,{ 
					'kebijakan_id' 		: keg.kebijakan_id.id,
					'program_id' 		: keg.program_id.id,
					'kegiatan_id' 		: keg.id,
					'indikator' 		: '',
					'target_capaian' 	: 0.0,
					'target_capaian_uom': False,
					'anggaran' 			: 0.0,
					'rka_coa_ids'		: rka_coa_ids
				}) )
		
		data = {
			'alokasi'			: 0.0,
			'anggaran'			: 0.0,
			'realisasi'			: 0.0,
			'sisa'		 		: 0.0, 
			'definitif'			: 0.0,
			'rka_kegiatan_ids'  : rka_kegiatan_ids,
			'state'			 	: RKA_STATES[0][0],
			'note'		 		: '',
			'mak_terisi' 		: True 
		}
		self.write(cr, uid, ids[0], data, context=context)	
		return 

	def copy(self, cr, uid, id, default=None, context=None):
		default = dict(context or {})
		old = self.browse(cr, uid, id, context=context)

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
							'volume' 		 : rv.volume,
							'volume_uom'	 : rv.volume_uom.id
						}))
					rka_detail_ids.append( (0,0,{
						# 'rka_coa_id' 	: rd.rka_coa_id,
						'keterangan'	: rd.keterangan,
						'tarif'		 	: rd.tarif,
						'jumlah'		: rd.jumlah,
						'volume_total' 	: rd.volume_total,
						'rka_volume_ids': rka_volume_ids
					}))

				rka_coa_ids.append( (0,0, {
					# 'rka_kegiatan_id' 	: rc.rka_kegiatan_id.id,
					'mak_id'			: rc.mak_id.id,
					'total'		 		: rc.total,
					'sumber_dana_id'	: rc.sumber_dana_id.id,
					'bulan'				: rc.bulan,
					'rka_detail_ids'	: rka_detail_ids

				}) )

			rka_kegiatan_ids.append( (0,0,{ 
				'kebijakan_id' 		: fd.kebijakan_id.id,
				'program_id' 		: fd.program_id.id,
				'kegiatan_id' 		: fd.kegiatan_id.id,
				'indikator' 		: fd.indikator,
				'target_capaian' 	: fd.target_capaian,
				'target_capaian_uom': fd.target_capaian_uom.id or False,
				'anggaran' 			: fd.anggaran,
				'rka_coa_ids'		: rka_coa_ids
			}) )
		
		default.update({'rka_kegiatan_ids' : rka_kegiatan_ids })
		return super(rka, self).copy(cr, uid, id, default, context=context)

###########################################################################
#Level 2 : RKA Kegiatan
###########################################################################
class rka_kegiatan(osv.osv):
	@api.onchange('rka_coa_ids') 
	def on_change_rka_coa_ids(self):
		total = 0.0
		for coa in self.rka_coa_ids:
			total = total + coa.total
		print total 
		self.anggaran = total 

	
	# def hitung_total(self, array_coas):
	# 	total = 0.0 
	# 	for ar in array_coas:
	# 		total = total + ar['total']
	# 	return total 
	
	def hitung_realisasi(self, array_coas):
		realisasi = 0 
		for ar in array_coas:
			realisasi = realisasi + ar['realisasi']
		return realisasi 

	# def onchange_rka_coa(self, cr, uid, ids, rka_coa_ids ):
	# 	array_coas = self.resolve_o2m_commands_to_record_dicts(
	# 		cr, uid, 'rka_coa_ids', rka_coa_ids, ['total', '']
	# 	) 

	# 	print rka_coa_ids
	# 	print array_coas

	# 	results = {
	# 		'value' : {
	# 			'anggaran' : self.hitung_total(array_coas),
	# 		}
	# 	}

	# 	return results

	# def _ftotal(self, cr, uid, ids, field, arg, context=None):
	# 	results = {}
	# 	rka_kegiatans = self.browse(cr, uid, ids, context=context) 
	# 	for rka_kegiatan in rka_kegiatans:
	# 		array_coas = rka_kegiatan.rka_coa_ids
	# 		results[rka_kegiatan.id] = self.hitung_total(array_coas)
	# 	return results


	def _frealisasi(self, cr, uid, ids, field, arg, context=None):
		results = {}
		rka_kegiatans = self.browse(cr, uid, ids, context=context) 

		# ambil satu-per-satu sesion object 
		for rka_kegiatan in rka_kegiatans:
			array_coas = rka_kegiatan.rka_coa_ids
			results[rka_kegiatan.id] = self.hitung_realisasi(array_coas)
		return results


	def _fsisa(self, cr, uid, ids, field, arg, context=None):
		results = {}
		rka_kegiatans = self.browse(cr, uid, ids, context=context) 

		# ambil satu-per-satu sesion object 
		for rka_kegiatan in rka_kegiatans:
			results[rka_kegiatan.id] = rka_kegiatan.anggaran - rka_kegiatan.realisasi
		return results


	_name 		= "anggaran.rka_kegiatan"
	_rec_name   = "kegiatan_id"
	_columns 	= {
		rka_id = fields.many2one('anggaran.rka', 'RKA')
		kebijakan_id = fields.many2one('anggaran.kebijakan', _('Kebijakan'))
		'category_id'  : fields.related('kebijakan_id' , 'category_id', type="many2one", 
			relation="anggaran.category", string=_("Kategori Kebijakan"), store=True),
		program_id = fields.many2one('anggaran.program', _('Program'))
		kegiatan_id = fields.many2one('anggaran.kegiatan', _('Kegiatan'))

		'unit_id'		  : fields.related('rka_id', 
			'unit_id',  type="many2one", 
			relation="anggaran.unit", 
			string="Unit", readonly=True ),

		indikator = fields.text(_('Indikator'))
		target_capaian = fields.float(_('Target Capaian'))
		target_capaian_uom = fields.many2one('product.uom', _('Satuan Target'))

		#		anggaran = fields.function(_ftotal, type='float', string="Total Anggaran", store=True)
		anggaran = fields.float("Total Anggaran")
		realisasi = fields.function(_frealisasi, type='float', string="Realisasi")
		sisa = fields.function(_fsisa, type='float', string="Sisa")
		definitif = fields.float("Definitif")

		rka_coa_ids = fields.one2many('anggaran.rka_coa','rka_kegiatan_id'
			_('Rincian'), ondelete="cascade")
	}


###########################################################################
#Level 3 : RKA Rincian MAK
###########################################################################
class rka_coa(osv.osv):
	_rec_name   = "mak_id"
	_name 		= "anggaran.rka_coa"

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


	def _frealisasi(self, cr, uid, ids, field, arg, context=None):
		results = {}
		rka_coas = self.browse(cr, uid, ids, context=context) 

		for rka_coa in rka_coas:
			results[rka_coa.id] = 0.0

			for rka_detail in rka_coa.rka_detail_ids:
				if rka_detail.realisasi > 0:
					results[rka_coa.id] += rka_detail.realisasi

		return results

	def _fsisa(self, cr, uid, ids, field, arg, context=None):
		results = {}
		rka_coas = self.browse(cr, uid, ids, context=context) 

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

	def calculate_total(self, cr, uid, ids, rka_detail_ids):
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

	_columns 	= {
		rka_kegiatan_id = fields.many2one('anggaran.rka_kegiatan', 'Kegiatan')
		mak_id = fields.many2one('anggaran.mata_anggaran_kegiatan', 'MAK')
		total = fields.float('Total')

		#diupdate waktu SPP confirm
		realisasi = fields.float('Realisasi')
		#		sisa = fields.float('Sisa')

		#		realisasi = fields.function(_frealisasi, type='float', string="Realisasi", )
		sisa = fields.function(_fsisa, type='float', string="Sisa")

		definitif = fields.float('Definitif Biaya')
		sumber_dana_id = fields.many2one('anggaran.sumber_dana', 'Sumber Dana')
		bulan = fields.many2one('account.period', 'Bulan')
		'rka_detail_ids'	: fields.one2many('anggaran.rka_detail','rka_coa_id','Detail', ondelete="cascade")

	}


###########################################################################
#Level 4: detail MAK
###########################################################################
class rka_detail(osv.osv):
	_rec_name   = "keterangan"
	_name 		= "anggaran.rka_detail"

	@api.onchange('rka_volume_ids','tarif') 
	def on_change_rka_volume_ids(self):
		total = 1
		for vol in self.rka_volume_ids:
			total = total * vol.volume
		self.jumlah = total 	
		self.volume_total = total * self.tarif	



	def _fsisa(self, cr, uid, ids, field, arg, context=None):
		results = {}
		rka_details = self.browse(cr, uid, ids, context=context) 

		# ambil satu-per-satu sesion object 
		for rka_detail in rka_details:
			if rka_detail.volume_total > 0:
				results[rka_detail.id] = rka_detail.volume_total - rka_detail.realisasi
			else:
				results[rka_detail.id] = 0.0

		return results

	# cari total spp detail MAK ini...
	def hitung_realisasi(self, cr, uid, rka_detail ):
		return 99.0

	def _frealisasi(self, cr, uid, ids, field, arg, context=None):
		results = {}
		rka_details = self.browse(cr, uid, ids, context=context) 

		# ambil satu-per-satu rka_detail object 
		for rka_detail in rka_details:
			if rka_detail.volume_total > 0:
				results[rka_detail.id] = self.hitung_realisasi(cr, uid, rka_detail )
			else:
				results[rka_detail.id] = 0.0

		return results


	_columns 	= {
		kebijakan_id = fields.related('rka_coa_id','rka_kegiatan_id', 'kegiatan_id' , 'program_id', 'kebijakan_id'
			type="many2one", relation="anggaran.kebijakan", string="Kebijakan", store=True),
		program_id = fields.related('rka_coa_id','rka_kegiatan_id', 'kegiatan_id' , 'program_id'
			type="many2one", relation="anggaran.program", string="Program", store=True),
		'kegiatan_id'    : fields.related('rka_coa_id','rka_kegiatan_id', 'kegiatan_id' , 
			type="many2one", relation="anggaran.kegiatan", string="Kegiatan", store=True),
		'unit_id'        : fields.related('rka_coa_id','rka_kegiatan_id', 'unit_id' , 
			type="many2one", relation="anggaran.unit", string="Unit", store=True),

		tahun = fields.related('rka_coa_id','rka_kegiatan_id', 'rka_id' , 'tahun'
			type="many2one", relation="account.fiscalyear", string="Tahun", store=True),

		period_id = fields.related('rka_coa_id','rka_kegiatan_id', 'rka_id' , 'period_id'
			type="many2one", relation="account.period", string="Period", store=True),

		rka_coa_id = fields.many2one('anggaran.rka_coa', _('MAK'))
		keterangan = fields.text(_('Keterangan'), required=True)
		tarif = fields.float(_('Tarif'), required=True)
		jumlah = fields.float(_('Jumlah'), required=True)

		'volume_total' 	: fields.float(_('Volume Total') , required=True),		
		realisasi = fields.float('Realisasi')
		sisa = fields.float('Sisa')
		#		realisasi = fields.function(_frealisasi, type='float', string='Realisasi', store=True)
		#		sisa = fields.function(_fsisa, type='float', string="Sisa", store=True)
		definitif = fields.float('Definitif Biaya')

		rka_volume_ids = fields.one2many('anggaran.rka_volume','rka_detail_id'
			_('Volumes'), ondelete="cascade")
	}

	def hitung_jumlah(self, array_volumes):
		jumlah = 1.0 
		for ar in array_volumes:
			jumlah = jumlah * ar['volume']
		return jumlah 

	def hitung_volume_total(self, array_volumes, tarif):
		jumlah = self.hitung_jumlah(array_volumes) 
		return jumlah * tarif

	def onchange_volumes(self, cr, uid, ids, rka_volume_ids, tarif):
		array_volumes = self.resolve_o2m_commands_to_record_dicts(
			cr, uid, 'rka_volume_ids', rka_volume_ids, ['volume']
		)

		print array_volumes

		# return harus berupa dict yang berisi key = 'value'
		# setiap value berupa dict yang berisi nilai dari field lain
		#   yang mau diupdate 

		results = {
			'value' : {
				'jumlah' : self.hitung_jumlah(array_volumes),
				'volume_total' : self.hitung_volume_total(array_volumes, tarif)
			}
		}

		return results


###########################################################################
#Level 5: detail volumes
###########################################################################
class rka_volume(osv.osv):
	_name 		= "anggaran.rka_volume"
	_columns 	= {
		rka_detail_id = fields.many2one('anggaran.rka_detail', 'RKA Detail')
		volume = fields.float('Volume')
		volume_uom = fields.many2one('product.uom', 'Satuan Volume')
	}


			

	
