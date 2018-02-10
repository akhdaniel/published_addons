from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class program(osv.osv):
	_name 		= "anggaran.program"
	_columns 	= {
		'name'      : fields.text('Nama'),
		'code'      : fields.char('Kode'),
		'kebijakan_id' : fields.many2one('anggaran.kebijakan', 'Kebijakan', required=True),
		'category_id'  : fields.related('kebijakan_id' , 'category_id', type="many2one", 
			relation="anggaran.category", string=_("Kategori Kebijakan"), store=True),
		'kegiatan_ids' : fields.one2many('anggaran.kegiatan','program_id','Kegiatans', ondelete="cascade")
	}

	def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		ids = []
		if name:
			ids = self.search(cr, user, ['|',('name', operator, name),('code', operator, name)] + args, limit=limit)
		else:
			ids = self.search(cr, user, args, context=context, limit=limit)
		return self.name_get(cr, user, ids, context=context)



	def name_get(self, cr, uid, ids, context=None):
		if not ids:
			return []
		if isinstance(ids, (int, long)):
					ids = [ids]
		reads = self.read(cr, uid, ids, ['name', 'code'], context=context)
		res = []
		for record in reads:
			name = record['name']
			if record['code']:
				name = record['code'] + ' ' + name
			res.append((record['id'], name))
		return res
