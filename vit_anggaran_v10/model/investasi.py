from odoo import tools
from odoo import fields,models
import openerp.addons.decimal_precision as dp
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)
INVESTASI_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]

class investasi(models.Model):
	_name 		= 'anggaran.investasi'
	name = fields.Char('Nomor', required=True, readonly=True)
	tanggal = fields.Date('Tanggal', required=True)
	unit_id = fields.Many2one('anggaran.unit', 'Unit Kerja')
	tahun_id = fields.Many2one('anggaran.fiscalyear', 'Tahun')
	period_id = fields.Many2one('anggaran.period', 'Perioda')
	#		keperluan = fields.Many2one('anggaran.rka_kegiatan', 'Untuk Keperluan')
	kepada_partner_id = fields.Many2one('res.partner', 'Dibayarkan Kepada', help="Partner (Supplier/Perorangan) penerima")
	keperluan = fields.Text("Keperluan")
	total = fields.Float("Total Biaya")

	pumkc_id = fields.Many2one('hr.employee', 'PUMKC')
	nip_pumkc = fields.Related('pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP PUMKC', store=True, readonly=True)
	atasan_pumkc_id = fields.Many2one('hr.employee', 'Atasan Langsung PUMKC')
	nip_atasan_pumkc = fields.Related('atasan_pumkc_id', 'otherid' , type='char', relation='hr.employee', string='NIP Atasan PUMKC', store=True, readonly=True)

	user_id = fields.Many2one('res.users', 'Created', required=True,readonly=True)
	state = fields.Selection(INVESTASI_STATES,'Status',readonly=True,required=True)

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

	def create(self, vals):
		#if context is None:
		#	context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.env['ir.sequence'].get('anggaran.investasi') or '/'
		new_id = super(investasi, self).create(vals)
		return new_id



class investasi_line(models.Model):
	_name 		= "anggaran.investasi_line"

	# def _sudah_sptb_search(self, obj, name, args):
	# 	#########################################################
	# 	# return list of tuples [('id','in',[1,2,3,4])]
	# 	# dimana 1,2,3,4 adalah id record yang mathcing dengan 
	# 	# yang dicari (misalnya yang sudah di-sptb, mana aja id nya)
	# 	#########################################################
	# 	data = [('sptb_line_ids','!=',False)]
	# 	res = self.search(data)
	# 	if not res:
	# 		return [('id', '=', 0)]
	# 	return [('id', 'in', [x[0] for x in res])]
	investasi_id = fields.Many2one('anggaran.investasi', 'Biaya')
	rka_coa_id = fields.Many2one('anggaran.rka_coa', 'COA Bersangkutan')
	investasi_ini = fields.Float("Jumlah")
	uraian = fields.Char('Uraian')

