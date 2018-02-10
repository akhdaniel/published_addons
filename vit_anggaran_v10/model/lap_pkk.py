from odoo import tools
from odoo import fields,models
import openerp.addons.decimal_precision as dp
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)
LAP_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class lap_pkk(models.Model):
	_name 		= "anggaran.lap_pkk"
	name = fields.Char('Nomor', required=True, readonly=True)
	unit_id = fields.Many2one('anggaran.unit', 'Unit')
	tahun_id = fields.Many2one('anggaran.fiscalyear', 'Tahun')
	rka_kegiatan_id = fields.Many2one('anggaran.rka_kegiatan', 'Kegiatan')
	kebijakan_id = fields.Related('rka_kegiatan_id', 'kebijakan_id' , type="many2one", relation="anggaran.kebijakan", string="Kebijakan", store=True)
	program_id = fields.Related('rka_kegiatan_id', 'kegiatan_id' , 'program_id', type="many2one", relation="anggaran.program", string="Program", store=True)
	state = fields.Selection(LAP_STATES,'Status',readonly=True,required=True)
	lap_pkk_line_ids 	= fields.One2many('anggaran.lap_pkk_detail','lap_pkk_id','Label', ondelete="cascade")

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

	def create(self, vals):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.env['ir.sequence'].get('anggaran.lap_pkk') or '/'
		new_id = super(biaya, self).create(vals)
		return new_id

class lap_pkk_detail(models.Model):
	_name 		= "anggaran.lap_pkk_detail"
	lap_pkk_id = fields.Many2one('anggaran.lap_pkk', 'Lap PKK')
	input_rencana = fields.Float("Input Rencana")
	input_realisasi = fields.Float("Input Realisasi")
	proses_rencana = fields.Float("Input Rencana")
	proses_realisasi = fields.Float("Input Realisasi")
	output_rencana = fields.Float("Input Rencana")
	output_realisasi = fields.Float("Input Realisasi")
	cap_thn_lalu_rencana = fields.Float("Capaian Tahun Lalu Rencana")
	cap_thn_lalu_realisasi = fields.Float("Capaian Tahun Lalu Realisasi")
	pct_capaian_target = fields.Float("Persen Capaian Target Renstra")
	outcome = fields.Float("Outcome")


