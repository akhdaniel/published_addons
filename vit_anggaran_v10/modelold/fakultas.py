from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class fakultas(osv.osv):
	_name 		= "anggaran.fakultas"
	_columns 	= {
		'code'		:	fields.char(_('Kode'), required=True),
		'name'		:	fields.char(_('Nama'), required=True),
		'alamat'	:	fields.char(_('Alamat')),
		'nama_bank'	:	fields.char(_('Nama Bank')),
		'nomor_rek'	:	fields.char(_('No Rekening')),
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
