from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class lap_pdana(osv.osv):
	_name 		= "anggaran.lap_pdana"
	_columns 	= {
		'unit_id'  			: fields.many2one('anggaran.unit', 'Unit'),
		'tahun_id'  		: fields.many2one('account.fiscalyear', 'Tahun'),
		'rka_coa_id' 		: fields.many2one('rka_coa_id', 'No Akun'),
		'kebijakan_id'		: fields.related('rka_coa_id', 'rka_kegiatan_id' , 'kebijakan_id',
								type="many2one", relation="anggaran.kebijakan", string="Kebijakan", store=True),
		'anggaran'  		: fields.related('rka_coa_id', 'total' , 
								type="float", relation="anggaran.rka_coa", string="Anggaran", store=True),
		'realisasi_bln_ini' : fields.float("Realisasi Bulan Ini"),
		'realisasi_sd_bln_ini' : fields.float("Realisasi sd. Bulan Ini"),
	}