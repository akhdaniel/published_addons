from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
INVESTASI_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class investasi(osv.osv):
	_name 		= 'anggaran.investasi'
	_columns 	= {
		'name' 				: fields.char('Nomor', required=True, readonly=True),
		'tanggal' 			: fields.date('Tanggal', required=True),
		'unit_id'	 		: fields.many2one('anggaran.unit', 'Unit Kerja'),
		'tahun_id'		    : fields.many2one('account.fiscalyear', 'Tahun'),
		'period_id'		    : fields.many2one('account.period', 'Perioda'),
		# 'keperluan'  		: fields.many2one('anggaran.rka_kegiatan', 'Untuk Keperluan'),
		'kepada_partner_id'	: fields.many2one('res.partner', 'Dibayarkan Kepada', help="Partner (Supplier/Perorangan) penerima"),
		'keperluan'			: fields.text("Keperluan"),
		'total' 			: fields.float("Total Biaya"),

		'pumkc_id'     		: fields.many2one('hr.employee', 'PUMKC'),
		'nip_pumkc' 		: fields.related('pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True),
		'atasan_pumkc_id'  	: fields.many2one('hr.employee', 'Atasan Langsung PUMKC'),
		'nip_atasan_pumkc' 	: fields.related('atasan_pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True),

		'user_id'	    	: fields.many2one('res.users', 'Created', required=True,readonly=True),
		'state'             : fields.selection(INVESTASI_STATES,'Status',readonly=True,required=True),
	}
	_defaults = {
		'state'       	: INVESTASI_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',		
	}
	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':INVESTASI_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':INVESTASI_STATES[1][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':INVESTASI_STATES[2][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':INVESTASI_STATES[3][0]},context=context)

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.investasi') or '/'
		new_id = super(investasi, self).create(cr, uid, vals, context=context)
		return new_id



class investasi_line(osv.osv):
	_name 		= "anggaran.investasi_line"

	# def _sudah_sptb_search(self, cr, uid, obj, name, args, context=None):
	# 	#########################################################
	# 	# return list of tuples [('id','in',[1,2,3,4])]
	# 	# dimana 1,2,3,4 adalah id record yang mathcing dengan 
	# 	# yang dicari (misalnya yang sudah di-sptb, mana aja id nya)
	# 	#########################################################
	# 	data = [('sptb_line_ids','!=',False)]
	# 	res = self.search(cr, uid, data, context=context)
	# 	if not res:
	# 		return [('id', '=', 0)]
	# 	return [('id', 'in', [x[0] for x in res])]

	_columns 	= {
		'investasi_id' 		: fields.many2one('anggaran.investasi', 'Biaya'),
		'rka_coa_id' 	: fields.many2one('anggaran.rka_coa', 'COA Bersangkutan'),
		'investasi_ini'  	: fields.float("Jumlah"),
		'uraian'  		: fields.char('Uraian'),

	}
