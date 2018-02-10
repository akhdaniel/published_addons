from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class jurusan(osv.osv):
	_name 		= "anggaran.jurusan"
	_columns 	= {
		'code'        : fields.char(_('Kode'), required=True),
		'name'        : fields.char(_('Nama'), required=True),
		'jurusan_id'  : fields.many2one('anggaran.jurusan', _('Jurusan'), required=False),
		'fakultas_id' : fields.many2one('anggaran.fakultas', _('Fakultas'), required=True),
		'income_ids'  : fields.one2many('anggaran.jurusan_income','jurusan_id','Incomes', ondelete="cascade"),
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


class jurusan_income(osv.osv):
	_name 		= "anggaran.jurusan_income"

	def _ftotal_spp(self, cr, uid, ids, field, arg, context=None):
		results = {}

		for inc in self.browse(cr, uid, ids, context=context):
			results[inc.id] = inc.jumlah * inc.tarif_spp

		return results	

	def _ftotal_bpp(self, cr, uid, ids, field, arg, context=None):
		results = {}

		for inc in self.browse(cr, uid, ids, context=context):
			results[inc.id] = inc.jumlah * inc.tarif_bpp

		return results	

	def _ftotal(self, cr, uid, ids, field, arg, context=None):
		results = {}

		for inc in self.browse(cr, uid, ids, context=context):
			results[inc.id] = inc.total_bpp + inc.total_spp

		return results	

	_columns 	= {
		'jurusan_id'		: fields.many2one('anggaran.jurusan', 'Jurusan'),
		'tahun_akademik'	: fields.many2one('anggaran.tahun_akademik', 'Tahun Akademik'),
		'angkatan'			: fields.many2one('anggaran.tahun_akademik', 'Angkatan'),
		'jumlah'			: fields.integer('Jumlah Mhs. Aktif'),
		'tarif_bpp'			: fields.integer('Tarif BPP'),
		'tarif_spp'			: fields.integer('Tarif SPP'),

		'total_bpp'			: fields.function(_ftotal_bpp, type='integer', string="Total BPP"),
		'total_spp'			: fields.function(_ftotal_spp, type='integer', string="Total SPP"),
		'total'				: fields.function(_ftotal, type='integer', string="Total"),
	}

class tahun_akademik(osv.osv):
	_name 		= "anggaran.tahun_akademik"

	_columns 	= {
		'code'	: fields.char("Code"),
		'name'	: fields.char("Tahun Akademik")
	}


