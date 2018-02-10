from openerp import tools
from openerp import api
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)

class mata_anggaran_kegiatan(osv.osv):
	_name = "anggaran.mata_anggaran_kegiatan"
	_description = 'mata anggaran kegiatan'
	_columns = {
		'name'				: fields.char(_('Nama'), size=64, required=False, readonly=False),
		'code'				: fields.char(_('Kode'), size=64, required=False, readonly=False),
		'kebijakan_id'	   	: fields.many2one('anggaran.kebijakan', _('Kebijakan'),  required=True,),
		'category_id'  		: fields.related('kebijakan_id' , 'category_id', type="many2one", 
			relation="anggaran.category", string=_("Kategori Kebijakan"), store=True),

		'program_id'	   	: fields.many2one('anggaran.program', _('Program'),  required=True,),
		'kegiatan_id' 		: fields.many2one('anggaran.kegiatan', _('Kegiatan'),  required=True,),
		'unit_id' 			: fields.many2one('anggaran.unit', _('Unit Kerja'),  required=True,),
		'cost_type_id'		: fields.many2one('anggaran.cost_type', _('Cost type') ,  required=True,),
		'coa_id'   			: fields.many2one('account.account', _('COA') )
	}

	@api.onchange('unit_id','kegiatan_id','cost_type_id') # if these fields are changed, call method
	def on_change(self):
		if self.kegiatan_id.code != False and self.cost_type_id != False and self.unit_id != False:
			self.code = '650.1.%s.%s.%s'  % (self.kegiatan_id.code , self.cost_type_id.code , self.unit_id.code )
			self.name = self.cost_type_id.name 

	def name_search(self, cr, user, name, args=None, operator='ilike', context=None, limit=100):
		if not args:
			args = []
		ids = []
		if name:
			ids = self.search(cr, user, [('code', operator, name)] + args, limit=limit)
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
