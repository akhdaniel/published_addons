from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
SC_STATES =[('draft','Draft'),('open','Open'), ('done','Done')]


class stock_card(osv.osv):
	_name 		= "vit.stock_card"
	_res_name 	= "product_id"
	_columns 	= {
		"ref"				: fields.char("Number"),
		"date_start"		: fields.date("Date Start"),
		"date_end"			: fields.date("Date End"),
		"location_id"		: fields.many2one('stock.location', 'Location'),
		"product_id"		: fields.many2one('product.product', 'Product'),
		"line_ids"			: fields.one2many('vit.stock_card_line','stock_card_id','Details', ondelete="cascade"),
		"state"				: fields.selection(SC_STATES,'Status',readonly=True,required=True),
		"user_id"			: fields.many2one('res.users', 'Created'),
	}

	_defaults = {
		'date_start'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'date_end'     		: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'			: lambda obj, cr, uid, context: uid,
		'ref'				: lambda obj, cr, uid, context: '/',		
		"state"				: "draft",
	}	


	def action_calculate(self,cr,uid,ids,context=None):
		# kosongkan stock_card_line
		# cari stock move product_id dan location_id, start_date to end_date
		# insert into stock_card_line
		# jika keluar dari location (source_id) maka isi ke qty_out
		# jika masu ke location (dest_id) maka isi ke qty_in
		# hitung qty_balance = qty_start + qty_in - qty_out 
		# start balance dihitung dari total qty stock move sebelum start_date

		stock_move = self.pool.get('stock.move')
		stock_card_line = self.pool.get('vit.stock_card_line')
		product = self.pool.get('product.product')

		for sc in self.browse(cr, uid, ids, context=context):
			cr.execute("delete from vit_stock_card_line where stock_card_id=%s" % sc.id)

			qty_start = 0.0
			qty_balance = 0.0
			qty_in = 0.0
			qty_out = 0.0
			product_uom = False 


			## beginning balance in 
			sql = "select sum(product_uom_qty) from stock_move where product_id=%s and date < '%s' and location_dest_id=%s and state='done'" %(
				sc.product_id.id, sc.date_start, sc.location_id.id)
			cr.execute(sql)
			res = cr.fetchone()
			if res and res[0]!= None:
				qty_start = res[0]

			## beginning balance out
			sql = "select sum(product_uom_qty) from stock_move where product_id=%s and date < '%s' and location_id=%s and state='done'" %(
				sc.product_id.id, sc.date_start, sc.location_id.id)
			cr.execute(sql)
			res = cr.fetchone()
			if res and res[0]!= None:
				qty_start = qty_start - res[0]
			
			## product uom
			# import pdb;pdb.set_trace()
			prod = product.browse(cr, uid, [sc.product_id.id], context=context)
			product_uom = prod.uom_id 


			data = {
				"stock_card_id"	: sc.id,
				"date"			: False,
				"qty_start"		: False,
				"qty_in"		: False,
				"qty_out"		: False,
				"qty_balance"	: qty_start,	
				"product_uom_id": product_uom.id,	
			}
			stock_card_line.create(cr, uid, data, context=context)

			##mutasi
			sm_ids = stock_move.search(cr, uid, [
				'|',
				('location_dest_id','=',sc.location_id.id),
				('location_id','=',sc.location_id.id),
				('product_id', 	'=' , sc.product_id.id),
				('date', 		'>=', sc.date_start),
				('date', 		'<=', sc.date_end),
				('state',		'=', 'done'),

			], order='date asc', context=context)

			for sm in stock_move.browse(cr, uid, sm_ids, context=context):

				qty_in = 0.0
				qty_out = 0.0

				#uom conversion factor
				if product_uom.id != sm.product_uom.id:
					factor =  product_uom.factor / sm.product_uom.factor 
				else:
					factor = 1.0

				if sm.location_dest_id == sc.location_id:	#incoming, dest = location
					qty_in = sm.product_uom_qty  * factor				
				elif sm.location_id == sc.location_id:		#outgoing, source = location
					qty_out = sm.product_uom_qty * factor

				qty_balance = qty_start + qty_in - qty_out

				data = {
					"stock_card_id"	: sc.id,
					"move_id"		: sm.id,
					"picking_id"	: sm.picking_id.id,
					"date"			: sm.date,
					"qty_start"		: qty_start,
					"qty_in"		: qty_in,
					"qty_out"		: qty_out,
					"qty_balance"	: qty_balance,	
					"product_uom_id": product_uom.id,	
					"name"			: sm.name,
				}
				stock_card_line.create(cr, uid, data, context=context)
				qty_start = qty_balance
		return

	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':SC_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':SC_STATES[1][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':SC_STATES[2][0]},context=context)

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('ref', '/') == '/':
			vals['ref'] = self.pool.get('ir.sequence').get(cr, uid, 'vit.stock_card') or '/'
		new_id = super(stock_card, self).create(cr, uid, vals, context=context)
		return new_id


class stock_card_line(osv.osv):
	_name 		= "vit.stock_card_line"
	_columns 	= {
		"name"			: fields.char("Description"),
		"stock_card_id"	: fields.many2one('vit.stock_card_id', 'Stock Card'),
		"move_id"		: fields.many2one('stock.move', 'Stock Move'),
		"picking_id"	: fields.many2one('stock.picking', 'Picking'),
		"date"			: fields.date("Date"),
		"qty_start"		: fields.float("Start"),
		"qty_in"		: fields.float("Qty In"),
		"qty_out"		: fields.float("Qty Out"),
		"qty_balance"	: fields.float("Balance"),
		"product_uom_id": fields.many2one('product.uom', 'UoM'),
	}

