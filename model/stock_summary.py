from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
SC_STATES = [('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')]


class stock_summary(osv.osv):
	_name = "vit.stock_summary"
	_res_name = "product_id"
	_columns = {
		"ref"				: fields.char("Number"),
		"date_start"		: fields.date("Date Start"),
		"date_end"			: fields.date("Date End"),
		"location_id"		: fields.many2one('stock.location', 'Location'),
		"line_ids"			: fields.one2many( 'vit.stock_summary_line', 'stock_summary_id','Details', ondelete="cascade"),
		"state"				: fields.selection( SC_STATES, 'Status',readonly= True,required=True),
		"user_id"			: fields.many2one('res.users', 'Created'),
	}

	_defaults = {
		'date_start'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'date_end'     		: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'			: lambda obj, cr, uid, context: uid,
		'ref'				: lambda obj, cr, uid, context: '/',
		"state"				: "draft",
	}


	def action_calculate( self, cr, uid,ids,context=None):
		# kosongkan stock_summary_line
		# cari list produk yang ada stocknya di location id
		# cari stock move product_id dan location_id, start_date to end_date
		# insert into stock_summary_line
		# jika keluar dari location (source_id) maka isi ke qty_out
		# jika masu ke location (dest_id) maka isi ke qty_in
		# hitung qty_balance = qty_start + qty_in - qty_out 
		# start balance dihitung dari total qty stock move sebelum start_date

		stock_summary_line = self.pool.get('vit.stock_summary_line')
		product = self.pool.get('product.product')

		for sc in self.browse(cr, uid, ids, context=context):
			cr.execute("delete from vit_stock_summary_line where stock_summary_id=%s" % sc.id)

			summary = []
			# {
			# 	'product_id':False,
			# 	'product_uom_id':False,
			# 	'qty_start':False,
			# 	'qty_in':False,
			# 	'qty_out':False,
			# 	'qty_balance':False,
			# }

			###### beginning balance
			self.beginning_lines(cr, uid, stock_summary_line, sc, context=context)
			self.mutasi_lines(cr, uid, stock_summary_line, sc, context=context)



		return

	def beginning_lines(self, cr, uid, stock_summary_line, sc, context=None):

		date = "in_date < '%s'" % (sc.date_start)

		sql = "select product_id,\
	    		uom_id,\
	    		lot_id, \
	    		qty \
	    		from stock_quant as q \
	    	  	where %s and location_id = %s \
	    		order by product_id" % (
			date, sc.location_id.id)
		cr.execute(sql)

		res = cr.fetchall()
		if not res or res[0] == 'None':
			return

		old_product_id = False
		i = 0
		total_start = 0.0

		for beg in res:
			product_id = beg[0]


			### sub total produc
			if old_product_id != product_id and i != 0:
				data = {
					"name"				: "Sub Total %s" % (product_id),
					"stock_summary_id"	: sc.id,
					"product_id"		: False,
					"product_uom_id"	: False,
					"lot_id"			: False,
					"qty_start"			: total_start,
					"qty_in"			: 0,
					"qty_out"			: 0,
					"qty_balance"		: 0,
				}
				stock_summary_line.create(cr, uid, data, context=context)
				total_start = 0.0

			data = {
				"stock_summary_id"	: sc.id,
				"product_id"		: product_id,
				"product_uom_id"	: beg[1],
				"lot_id"			: beg[2],
				"qty_start"			: beg[3],
				"qty_in"			: 0,
				"qty_out"			: 0,
				"qty_balance"		: 0,
			}
			stock_summary_line.create(cr, uid, data, context=context)
			old_product_id = product_id
			total_start += beg[3]
			i += 1

	def mutasi_lines(self, cr, uid, stock_summary_line, sc, context=None):
		date = "in_date >= '%s' and in_date <= '%s'" % (sc.date_start, sc.date_end)

		sql = "select product_id,\
	    		uom_id,\
	    		lot_id, \
	    		qty \
	    		from stock_quant as q \
	    	  	where %s and location_id = %s \
	    		order by product_id" % (
			date, sc.location_id.id)
		cr.execute(sql)

		res = cr.fetchall()
		if not res or res[0] == 'None':
			return

		for mut in res:
			product_id = mut[0]
			qty_out = 0.0
			qty_in = 0.0
			if mut[3] < 0:
				qty_out = abs(mut[3])
			else:
				qty_in = mut[3]

			data = {
				"qty_in"		: qty_in,
				"qty_out"		: qty_out,
				"qty_balance"	: 0,
			}
			# line
			sql = "update vit_stock_summary_line set \
				qty_in = %s, qty_out = %s, qty_balance = %s \
				where product_id = %s and stock_summary_id=%s" %(qty_in,qty_out,0,product_id,sc.id)
			cr.execute(sql)

			#subtotal
			sql = "update vit_stock_summary_line set qty_in"


	def action_draft(self ,cr ,uid ,ids ,context=None):
		# set to "draft" state
		return self.write(cr ,uid ,ids ,{'state' :SC_STATES[0][0]} ,context=context)

	def action_confirm(self ,cr ,uid ,ids ,context=None):
		# set to "confirmed" state
		return self.write(cr ,uid ,ids ,{'state' :SC_STATES[1][0]} ,context=context)

	def action_done(self ,cr ,uid ,ids ,context=None):
		# set to "done" state
		return self.write(cr ,uid ,ids ,{'state' :SC_STATES[2][0]} ,context=context)

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('ref', '/') == '/':
			vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'vit.stock_summary') or '/'
		new_id = super(stock_summary, self).create(cr, uid, vals, context=context)
		return new_id


class stock_summary_line(osv.osv):
	_name 		= "vit.stock_summary_line"
	_columns 	= {
		"name"			: fields.char("Description"),
		"stock_summary_id"	: fields.many2one('vit.stock_summary_id', 'Stock Card'),
		"product_id"	: fields.many2one('product.product', 'Product'),
		"product_uom_id": fields.many2one('product.uom', 'UoM'),
		"lot_id"		: fields.many2one('stock.production.lot', 'Serial Number'),
		"expired_date"	: fields.related('lot_id','life_date', type='date',
							relation='stock.production.lot',
							string='ED',
							store=True),
		"qty_start"		: fields.float("Start"),
		"qty_in"		: fields.float("Qty In"),
		"qty_out"		: fields.float("Qty Out"),
		"qty_balance"	: fields.float("Balance"),
	}

