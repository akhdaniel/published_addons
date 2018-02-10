from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
LAP_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class lap_pkk(osv.osv):
	_name 		= "anggaran.lap_pkk"
	_columns 	= {
		'name' 					: fields.char('Nomor', required=True, readonly=True),
		'unit_id'  				: fields.many2one('anggaran.unit', 'Unit'),
		'tahun_id'  			: fields.many2one('account.fiscalyear', 'Tahun'),
		'rka_kegiatan_id' 		: fields.many2one('anggaran.rka_kegiatan', 'Kegiatan'),
		'kebijakan_id'			: fields.related('rka_kegiatan_id', 'kebijakan_id' , type="many2one", relation="anggaran.kebijakan", string="Kebijakan", store=True),
		'program_id'			: fields.related('rka_kegiatan_id', 'kegiatan_id' , 'program_id', type="many2one", relation="anggaran.program", string="Program", store=True),
		'state'             	: fields.selection(LAP_STATES,'Status',readonly=True,required=True),
		'lap_pkk_line_ids'		: fields.one2many('anggaran.lap_pkk_detail','lap_pkk_id','Label', ondelete="cascade")
	}
	_defaults = {
		'state'       	: LAP_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',		
	}
	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':LAP_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':LAP_STATES[1][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':LAP_STATES[2][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':LAP_STATES[3][0]},context=context)

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.lap_pkk') or '/'
		new_id = super(biaya, self).create(cr, uid, vals, context=context)
		return new_id

class lap_pkk_detail(osv.osv):
	_name 		= "anggaran.lap_pkk_detail"
	_columns 	= {
		'lap_pkk_id'			: fields.many2one('anggaran.lap_pkk', 'Lap PKK'),
		'input_rencana'			: fields.float("Input Rencana"),
		'input_realisasi'		: fields.float("Input Realisasi"),
		'proses_rencana'		: fields.float("Input Rencana"),
		'proses_realisasi'		: fields.float("Input Realisasi"),
		'output_rencana'		: fields.float("Input Rencana"),
		'output_realisasi'		: fields.float("Input Realisasi"),
		'cap_thn_lalu_rencana' 	: fields.float("Capaian Tahun Lalu Rencana"),
		'cap_thn_lalu_realisasi': fields.float("Capaian Tahun Lalu Realisasi"),
		'pct_capaian_target' 	: fields.float("Persen Capaian Target Renstra"),
		'outcome' 				: fields.float("Outcome"),
	}

