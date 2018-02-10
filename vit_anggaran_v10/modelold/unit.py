from openerp import tools
from openerp.osv import fields,osv
from openerp import api
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class unit(osv.osv):
	_name 		= "anggaran.unit"
	_columns 	= {
		'code':	fields.char('Kode', required=True, select=True),
		'name':	fields.char('Nama', required=True),
		'fakultas_id' : fields.many2one('anggaran.fakultas', 'Fakultas'),
		'jurusan_id'  : fields.many2one('anggaran.jurusan', 'Jurusan'),
		'company_id'  : fields.many2one('res.company', 'Universitas', required=True),
	}

	@api.onchange('fakultas_id','jurusan_id') # if these fields are changed, call method
	def on_change(self):

		if self.jurusan_id.id != False :
			self.code = '%s'  % (self.jurusan_id.code  )
			self.name = 'Unit Kerja %s' % (self.jurusan_id.name )
		
		elif self.fakultas_id.id != False :
			self.code = '%s'  % (self.fakultas_id.code  )
			self.name = 'Unit Kerja Fakultas %s' % (self.fakultas_id.name )

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
