from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
BIAYA_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class biaya(osv.osv):
	_name 		= 'anggaran.biaya'
	_columns 	= {
		'name' 				: fields.char('Nomor', required=True, readonly=True),
		'tanggal' 			: fields.date('Tanggal', required=True),
		'unit_id'	 		: fields.many2one('anggaran.unit', 'Unit Kerja'),
		'tahun_id'		    : fields.many2one('account.fiscalyear', 'Tahun'),
		'kas_id'		    : fields.many2one('anggaran.kas', 'Kas Keluar', domain=[('type','=','out')]),
		'keperluan'  		: fields.many2one('anggaran.rka_kegiatan', 'Untuk Keperluan'),
		'total' 			: fields.float("Total Biaya"),
		'kepada_partner_id'	: fields.many2one('res.partner', 'Dibayarkan Kepada', help="Partner (Supplier/Perorangan) penerima"),

		'biaya_line_ids' 	: fields.one2many('anggaran.biaya_line','biaya_id','Penjelasan', 
								ondelete="cascade"),

		'pumkc_id'     		: fields.many2one('hr.employee', 'PUMKC'),
		'nip_pumkc' 		: fields.related('pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True),
		'atasan_pumkc_id'  	: fields.many2one('hr.employee', 'Atasan Langsung PUMKC'),
		'nip_atasan_pumkc' 	: fields.related('atasan_pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True),

		'user_id'	    	: fields.many2one('res.users', 'Created', required=True,readonly=True),
		'state'             : fields.selection(BIAYA_STATES,'Status',readonly=True,required=True),
	}
	_defaults = {
		'state'       	: BIAYA_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',		
	}
	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':BIAYA_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':BIAYA_STATES[1][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':BIAYA_STATES[2][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':BIAYA_STATES[3][0]},context=context)

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.biaya') or '/'
		new_id = super(biaya, self).create(cr, uid, vals, context=context)
		return new_id



class biaya_line(osv.osv):
	_name 		= "anggaran.biaya_line"

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


	def _sudah_sptb(self, cr, uid, ids, name, arg, context=None):
		res = {}
		for biaya_line in self.browse(cr, uid, ids, context=context):
			res[biaya_line.id] = False
			if biaya_line.sptb_line_ids:
				res[biaya_line.id] = True
		return res

	_columns 	= {
		'biaya_id' 		: fields.many2one('anggaran.biaya', 'Biaya'),
		'rka_coa_id' 	: fields.many2one('anggaran.rka_coa', 'COA Bersangkutan'),
		'biaya_ini'  	: fields.float("Jumlah"),
		'uraian'  		: fields.char('Uraian'),

		'sptb_line_ids'	: fields.one2many('anggaran.sptb_line','biaya_line_id','SPTB Item'),
		'sudah_sptb'	: fields.function(_sudah_sptb, 
							string='Sudah di-SPTB-kan',  
						    type='boolean', 
						    #fnct_search=_sudah_sptb_search,
						    help="Apakah biaya ini sudah dicatatkan ke SPTB."),

	}
