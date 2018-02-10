from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class sumber_dana(osv.osv):
	_name 		= "anggaran.sumber_dana"
	_columns 	= {
		'code'   : fields.char("Kode"),
		'name'   : fields.char("Nama")
	}
