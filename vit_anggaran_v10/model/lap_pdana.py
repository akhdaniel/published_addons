from odoo import tools
from odoo import fields,models
import openerp.addons.decimal_precision as dp
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)

class lap_pdana(models.Model):
	_name 		= "anggaran.lap_pdana"
	unit_id = fields.Many2one('anggaran.unit', 'Unit')
	tahun_id = fields.Many2one('anggaran.fiscalyear', 'Tahun')
	rka_coa_id = fields.Many2one('rka_coa_id', 'No Akun')
	kebijakan_id = fields.Related('rka_coa_id', 'rka_kegiatan_id' , 'kebijakan_id', type="many2one", relation="anggaran.kebijakan", string="Kebijakan", store=True)
	anggaran = fields.Related('rka_coa_id', 'total' , type="float", relation="anggaran.rka_coa", string="Anggaran", store=True)
	realisasi_bln_ini = fields.Float("Realisasi Bulan Ini")
	realisasi_sd_bln_ini = fields.Float("Realisasi sd. Bulan Ini")
