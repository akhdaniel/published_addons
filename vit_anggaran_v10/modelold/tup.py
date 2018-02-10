from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
TUP_STATES =[ 	('draft','Draft'),
				('open','Verifikasi'), 
				('reject','Ditolak'),
                ('done','Disetujui')]

class tup(osv.osv):
	_name 		= 'anggaran.tup'
	_columns 	= {
		'name' 				: fields.char('Nomor' , readonly=True, required=True ),
		'tanggal' 			: fields.date('Tanggal', required=True),
		'tahun_id'		    : fields.many2one('account.fiscalyear', 'Tahun'),
		'lampiran'			: fields.integer('Lampiran'),
		'perihal' 			: fields.char('Perihal', required=True),
		'kepada'  			: fields.text('Kepada', required=True),
		'dasar_rkat' 		: fields.char('Dasar RKAT Nomor/Tanggal', required=True),
		'jumlah'  			: fields.float('Jumlah', required=True),
		'unit_id' 			: fields.many2one('anggaran.unit', 'Atas Nama', required=True),
		'nomor_rek' 		: fields.char('Nomor Rekening'),
		'nama_bank' 		: fields.char('Nama Bank'),

		'pumkc_id'     		: fields.many2one('hr.employee', 'PUMKC'),
		'nip_pumkc' 		: fields.related('pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True),
		'atasan_pumkc_id'   : fields.many2one('hr.employee', 'Atasan Langsung PUMKC'),
		'nip_atasan_pumkc' 	: fields.related('atasan_pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True),

		'state'             : fields.selection(TUP_STATES,'Status',readonly=True,required=True),
		'user_id'	    	: fields.many2one('res.users', 'Created'),
	}
	_defaults = {
		'state'       	: TUP_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',
	}

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.tup') or '/'
		new_id = tuper(tup, self).create(cr, uid, vals, context=context)
		return new_id
		
	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':TUP_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':TUP_STATES[1][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		#set to "reject" state
		return self.write(cr,uid,ids,{'state':TUP_STATES[2][0]},context=context)	
		
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':TUP_STATES[3][0]},context=context)

	def action_create_spm(self,cr,uid,ids,context=None):
		tup = self.browse(cr, uid, ids[0], context)
		spm_obj = self.pool.get("anggaran.spm")
		data = {
			'name' 			: '/',
			'tanggal' 		: time.strftime("%Y-%m-%d") ,
			'cara_bayar'    : 'up',
			'unit_id'	 	: tup.unit_id.id,
			'tahun_id'		: tup.tahun_id.id,
			'jumlah' 		: tup.jumlah,
			'sisa' 			: 0.0,
			'user_id'	    : uid, 
			'state'         : 'draft',
			'tup_id'		: tup.id
		}
		spm_id = spm_obj.create(cr,uid,data,context)
		return spm_id

