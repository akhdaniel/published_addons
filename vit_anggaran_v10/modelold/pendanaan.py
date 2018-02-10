from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
PENDANAAN_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class pendanaan(osv.osv):
	_name 		= 'anggaran.pendanaan'
	_columns 	= {
		'name' 				: fields.char('Nomor', required=True, readonly=True),
		'tanggal' 			: fields.date('Tanggal', required=True),
		'unit_id'	 		: fields.many2one('anggaran.unit', 'Unit Kerja'),
		'tahun_id'		    : fields.many2one('account.fiscalyear', 'Tahun'),
		'period_id'		    : fields.many2one('account.period', 'Period'),
		'keperluan'  		: fields.many2one('anggaran.rka_kegiatan', 'Untuk Keperluan'),
		'total' 			: fields.float("Total Pendanaan"),

		'pendanaan_line_ids' 	: fields.one2many('anggaran.pendanaan_line','pendanaan_id','Penjelasan', 
								ondelete="cascade"),

		'pumkc_id'     		: fields.many2one('hr.employee', 'PUMKC'),
		'nip_pumkc' 		: fields.related('pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True),
		'atasan_pumkc_id'  	: fields.many2one('hr.employee', 'Atasan Langsung PUMKC'),
		'nip_atasan_pumkc' 	: fields.related('atasan_pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True),

		'user_id'	    	: fields.many2one('res.users', 'Created', required=True,readonly=True),
		'state'             : fields.selection(PENDANAAN_STATES,'Status',readonly=True,required=True),
	}
	_defaults = {
		'state'       	: PENDANAAN_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',		
	}
	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':PENDANAAN_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':PENDANAAN_STATES[1][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':PENDANAAN_STATES[2][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':PENDANAAN_STATES[3][0]},context=context)

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.pendanaan') or '/'
		new_id = super(pendanaan, self).create(cr, uid, vals, context=context)
		return new_id



class pendanaan_line(osv.osv):
	_name 		= "anggaran.pendanaan_line"


	_columns 	= {
		'pendanaan_id' 		: fields.many2one('anggaran.pendanaan', 'Pendanaan'),
		'pendanaan_ini'  	: fields.float("Jumlah"),
		'uraian'  		: fields.char('Uraian'),

		'sudah_sptb'	: fields.function(_sudah_sptb, 
							string='Sudah di-SPTB-kan',  
						    type='boolean', 
						    #fnct_search=_sudah_sptb_search,
						    help="Apakah pendanaan ini sudah dicatatkan ke SPTB."),

	}
