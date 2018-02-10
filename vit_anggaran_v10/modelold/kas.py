from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
KAS_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class kas(osv.osv):
	_name 		= "anggaran.kas"

	def _biaya_exists(self, cursor, user, ids, name, arg, context=None):
		res = {}
		for kas in self.browse(cursor, user, ids, context=context):
			res[kas.id] = False
			if kas.biaya_ids:
				res[kas.id] = True
		return res

	_columns 	= {
		'name'   				: fields.char("Nomor", readonly=True ),
		'tanggal'				: fields.date("Tanggal", required=True),
		'tahun_id'		    	: fields.many2one('account.fiscalyear', 'Tahun', required=True),
		'unit_id' 				: fields.many2one('anggaran.unit', 'Unit Kerja', required=True, help="Unit Kerja yang memiliki transaksi ini"),
		'sumber_uang'       	: fields.selection([('up','UP'),('tup','TUP'),('gup','GUP')],
								'Sumber Uang', help="Dari UP, TUP, atau GUP"),
		'type'   				: fields.selection([('in','Masuk'),('out','Keluar')],'Jenis Kas',required=True),
		'jenis_item'   			: fields.selection([('um','Uang Muka'),('def','Definitif')],'Jenis Item',required=True),
		'journal_id' 			: fields.many2one('account.journal', 'Journal'),

		'kepada_unit_id' 		: fields.many2one('anggaran.unit', 'Dibayarkan Kepada Unit', help="Unit penerima uang kas keluar"),
		'dari_unit_id' 			: fields.many2one('anggaran.unit', 'Diterima Dari', help="Unit pengirim uang kas masuk"),
		'kepada_partner_id'	 	: fields.many2one('res.partner', 'Dibayarkan Kepada Partner', help="Partner (Supplier/Perorangan) penerima kas keluar"),

		'jumlah' 				: fields.float("Jumlah", required=True),
		'cheque_nomor'			: fields.char("Cheque Nomor"),
		'rek_nomor'				: fields.char("Rekening Nomor"),
		'kegiatan_id'  			: fields.many2one('anggaran.rka_kegiatan', 'Untuk Keperluan'),
		'dasar_pembayaran' 		: fields.char("Dasar Pembayaran"),

		'bendahara_id'     		: fields.many2one('hr.employee', 'Bendahara Penerima'),
		'nip_bendahara' 		: fields.related('bendahara_id', 'otherid' , type='char', relation='hr.employee', string='NIP Bendahara Penerima', store=True, readonly=True),
		'kadiv_anggaran_id'		: fields.many2one('hr.employee', 'Kepala Divisi Anggaran'),
		'nip_kadiv_anggaran'	: fields.related('kadiv_anggaran_id', 'otherid' , type='char', relation='hr.employee', string='NIP Kepala Divisi Anggaran', store=True, readonly=True),
		'kadiv_akuntansi_id'  	: fields.many2one('hr.employee', 'Kepala Divisi Akuntansi'),
		'nip_kadiv_akuntansi' 	: fields.related('kadiv_akuntansi_id', 'otherid' , type='char', relation='hr.employee', string='NIP Kepala Divisi Akuntansi', store=True, readonly=True),
		'dirkeu_id' 			: fields.many2one('hr.employee', 'Direktur Direktorat Keuangan'),
		'nip_dirkeu_id'			: fields.related('dirkeu_id', 'otherid' , type='char', relation='hr.employee', string='NIP Kepala Divisi Akuntansi', store=True, readonly=True),
		
		'state'             	: fields.selection(KAS_STATES,'Status',readonly=True,required=True),
		'user_id'	    		: fields.many2one('res.users', 'Created'),
		'spm_id' 				: fields.many2one('anggaran.spm', 'SPM Asal', help="SPM untuk Pengeluaran Kas"),

		'biaya_ids'				: fields.one2many('anggaran.biaya','kas_id','Biaya'),
		'biaya_exists'			: fields.function(_biaya_exists, 
			string='Biaya Sudah Tercatat',  
		    type='boolean', help="Apakah kas keluar ini sudah dicatatkan bukti biayanya."),

	} 
	_defaults = {
		'state'       	: KAS_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',		
	}

	def action_view_biaya(self, cr, uid, ids, context=None):
		'''
		This function returns an action that display existing biaya 
		of given kas ids. It can either be a in a list or in a form view, 
		if there is only one biaya to show.
		'''
		mod_obj = self.pool.get('ir.model.data')
		act_obj = self.pool.get('ir.actions.act_window')

		result = mod_obj.get_object_reference(cr, uid, 'anggaran', 'action_biaya_list')
		id = result and result[1] or False
		result = act_obj.read(cr, uid, [id], context=context)[0]
		#compute the number of biaya to display
		biaya_ids = []
		for kas in self.browse(cr, uid, ids, context=context):
			biaya_ids += [biaya.id for biaya in kas.biaya_ids]
		#choose the view_mode accordingly
		if len(biaya_ids)>1:
			result['domain'] = "[('id','in',["+','.join(map(str, biaya_ids))+"])]"
		else:
			res = mod_obj.get_object_reference(cr, uid, 'anggaran', 'view_biaya_form')
			result['views'] = [(res and res[1] or False, 'form')]
			result['res_id'] = biaya_ids and biaya_ids[0] or False
		return result

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.kas.%s' % vals['type'] ) or '/'
		new_id = super(kas, self).create(cr, uid, vals, context=context)
		return new_id

	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':KAS_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':KAS_STATES[1][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state

		# bentuk kas masuk di unit tujuan
		kas = self.browse(cr, uid, ids[0], context=context)
		if kas.kepada_unit_id:
			context.update({
				'tahun_id' 			: kas.tahun_id.id, 
				'dasar_pembayaran' 	: kas.dasar_pembayaran, 
				'jumlah' 			: kas.jumlah, 
				'unit_id' 			: kas.kepada_unit_id.id, 
				'contra_unit' 		: kas.unit_id.id, 
				'kegiatan_id' 		: kas.kegiatan_id.id,
				'jenis_item' 		: kas.jenis_item,
				'sumber_uang' 		: kas.sumber_uang,
				'spm_id' 			: kas.spm_id.id,
			})
			kas_id = self.create_kas(cr, uid, 'in', context )
		return self.write(cr,uid,ids,{'state':KAS_STATES[3][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':KAS_STATES[2][0]},context=context)

	def create_kas(self, cr, uid, type, context=None):

		#################################################################
		# cari journal kas keluar
		#################################################################
		journal_ids = False
		if type=='out':
			journal_ids = self.pool.get("account.journal").search(cr,uid,[('code','=','BNK2')], context=context)
			if not journal_ids:
				raise osv.except_osv(_('Error'),_("Journal untuk transaksi Kas Keluar tidak ditemukan") ) 
		elif type=='in':
			journal_ids = self.pool.get("account.journal").search(cr,uid,[('code','=','BNK2')], context=context)
			if not journal_ids:
				raise osv.except_osv(_('Error'),_("Journal untuk transaksi Kas Masuk tidak ditemukan") ) 

		data = {
			'name'   			: '/',
			'tanggal'			: time.strftime("%Y-%m-%d") ,
			'tahun_id' 			: context['tahun_id'],
			'unit_id' 			: context['unit_id'],
			'type'   			: type,
			'dasar_pembayaran' 	: context['dasar_pembayaran'], 
			'kegiatan_id' 		: context['kegiatan_id'], 
			'journal_id' 		: journal_ids[0],
			'kepada_unit_id' 	: context['contra_unit'] if type=='out' else False,
			'dari_unit_id' 		: context['contra_unit'] if type=='in' else False,
			'jumlah' 			: context['jumlah'],
			'jenis_item' 		: context['jenis_item'],
			'sumber_uang' 		: context['sumber_uang'],
			'spm_id' 			: context['spm_id'],
			'cheque_nomor'		: '',
			'rek_nomor'			: '',
			'state'             : 'draft',
			'user_id'	    	: uid, 
		}
		kas_id = self.create(cr, uid, data, context=context)
		return kas_id 

	def action_create_biaya(self, cr, uid, ids, context=None):
		kas = self.browse(cr, uid, ids[0], context=context)
		biaya = self.pool.get("anggaran.biaya")
		data = {
			'name' 				: '/',
			'tanggal' 			: time.strftime("%Y-%m-%d") ,
			'biaya_line_ids' 	: False,
			'tahun_id' 			: kas.tahun_id.id,
			'unit_id' 			: kas.unit_id.id,	  
			'kepada_partner_id' : kas.kepada_partner_id.id,	  
			'total'				: kas.jumlah,
			'kas_id'		    : kas.id,
			'user_id'	    	: uid, 
			'state'            	: 'draft'
		}
		biaya_id = biaya.create(cr, uid, data, context=context)
		return biaya_id
