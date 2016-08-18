from openerp import tools
from openerp.osv import fields, osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

_logger = logging.getLogger(__name__)
SC_STATES = [('draft', 'Draft'), ('open', 'Open'), ('done', 'Done')]


class stock_summary(osv.osv):
	_name = "vit.stock_summary"
	_rec_name = "location_id"
	_columns = {
		"ref"				: fields.char("Number"),
		"date_start"		: fields.date("Date Start"),
		"date_end"			: fields.date("Date End"),
		"location_id"		: fields.many2one('stock.location', 'Location'),
		"line_ids"			: fields.one2many( 'vit.stock_summary_line', 'stock_summary_id','Details', ondelete="cascade"),
		"breakdown_sn"		: fields.boolean("Breakdown Serial Number?"),
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

		for sc in self.browse(cr, uid, ids, context=context):
			cr.execute("delete from vit_stock_summary_line where stock_summary_id=%s" % sc.id)

			if sc.breakdown_sn:
				self.beginning_lines_sn(cr, uid, stock_summary_line, sc, context=context)
				self.mutasi_lines_sn(cr, uid, stock_summary_line, sc, context=context)
			else:
				self.beginning_lines_nosn(cr, uid, stock_summary_line, sc, context=context)
				self.mutasi_lines_nosn(cr, uid, stock_summary_line, sc, context=context)

			self.update_balance(cr, uid, sc, context=context)

		return


	def beginning_lines_sn(self, cr, uid, stock_summary_line, sc, context=None):
		line_type = "beg"
		self.process_lines_sn(cr, uid, line_type, stock_summary_line, sc, context=context)

	def mutasi_lines_sn(self, cr, uid, stock_summary_line, sc, context=None):
		line_type = "mut"
		self.process_lines_sn(cr, uid, line_type,  stock_summary_line, sc, context=context)


	def process_lines_sn(self,cr, uid,line_type,  stock_summary_line, sc, context=None):
		sql = "select \
			product_id, \
			uom_id,\
			qty,\
			lot_id, \
			in_date, \
			id \
			from stock_quant where \
			%s and \
			location_id %s"

		##########################################################################
		# fill product
		##########################################################################
		if line_type == "beg":
			self.fill_product_data(cr, uid, sql, stock_summary_line, sc, context=context)
			self.update_starting(cr, uid, sql, stock_summary_line, sc, context=context)

		return

		##########################################################################
		# update incoming: qty_in
		# outgoing: qty_out
		##########################################################################
		if line_type=="mut":
			self.update_incoming(cr, uid, sql, stock_summary_line, sc, context=context)
			self.update_outgoing(cr, uid, sql, stock_summary_line, sc, context=context)


		##########################################################################
		# sub total
		##########################################################################




	def fill_product_data(self,cr, uid, sql, stock_summary_line, sc, context=None):
		date  = "in_date <= '%s 24:00:00'"  % (sc.date_end)
		cr.execute(sql % (date, "=%s" % (sc.location_id.id)))
		res = cr.fetchall()
		if not res or res[0] == None:
			return False
		for beg in res:
			product_id = beg[0]
			product_uom_id = beg[1]
			lot_id = beg[3] if beg[3] is not None else False
			quant_id = beg[5]

			# cari stock move
			sql3 = "select qm.move_id from \
				stock_quant_move_rel qm \
				left join stock_move m on m.id = qm.move_id \
				where qm.quant_id=%s and \
				(m.location_dest_id=%s or m.location_id=%s)" %(
				quant_id, sc.location_id.id, sc.location_id.id)
			cr.execute(sql3)
			moves = cr.fetchall()
			if not moves or moves[0] == None:
				data = {
					"stock_summary_id": sc.id,
					"product_id"	: product_id,
					"product_uom_id"	: product_uom_id,
					"lot_id"			: lot_id,
					"stock_quant_id"	: quant_id,
					"stock_move_id"			: False
				}
				stock_summary_line.create(cr, uid, data, context=context)
			else:
				for move in moves:
					move_id = move[0]
					data = {
						"stock_summary_id"	: sc.id,
						"product_id"		: product_id,
						"product_uom_id"	: product_uom_id,
						"lot_id"			: lot_id,
						"stock_quant_id"	: quant_id,
						"stock_move_id"			: move_id
					}
					stock_summary_line.create(cr, uid, data, context=context)

	def update_starting(self, cr, uid, sql, stock_summary_line, sc, context=None):
		date = "write_date < '%s 00:00:00'" % (sc.date_start)
		cr.execute(sql % (date, "=%s"%(sc.location_id.id)))
		res = cr.fetchall()
		if not res or res[0] == None:
			return

		for beg in res:
			product_id = beg[0]
			sm_uom_id = beg[1]
			qty = beg[2]
			qty, product_uom_id = self.convert_uom_qty(cr, uid, product_id, sm_uom_id, qty, context=context)
			quant_id = beg[5]

			# cari stock move
			sql3 = "select qm.move_id,m.product_uom_qty from stock_quant_move_rel qm \
				left join stock_move m on m.id = qm.move_id \
				where qm.quant_id=%s" % (quant_id)
			cr.execute(sql3)
			moves = cr.fetchall()
			if not moves or moves[0] == None:
				sql2 = "update vit_stock_summary_line set \
							qty_start = %s \
							where stock_summary_id=%s and stock_quant_id = %s" % \
					   (qty, sc.id, quant_id)
				cr.execute(sql2)
			else:
				for move in moves:
					sql2 = "update vit_stock_summary_line set \
								qty_start = %s \
								where stock_summary_id=%s and stock_quant_id = %s and stock_move_id=%s" % \
						   (move[1], sc.id, quant_id, move[0])
					cr.execute(sql2)

	def update_incoming(self, cr, uid, sql, stock_summary_line, sc, context=None):
		date = "in_date >= '%s 00:00:00' and in_date <='%s 24:00:00'" % (sc.date_start,sc.date_end)
		cr.execute(sql % (date, "=%s"%(sc.location_id.id)))
		res = cr.fetchall()
		if not res or res[0] == 'None':
			return

		for beg in res:
			product_id = beg[0]
			sm_uom_id = beg[1]
			qty = beg[2]
			qty, product_uom_id = self.convert_uom_qty(cr, uid, product_id, sm_uom_id, qty, context=context)
			quant_id = beg[5]
			sql2 = "update vit_stock_summary_line set \
						qty_in = %s \
						where stock_summary_id=%s and stock_quant_id = %s" % \
				   (qty, sc.id, quant_id)
			cr.execute(sql2)

	def update_outgoing(self, cr, uid, sql, stock_summary_line, sc, context=None):
		date = "in_date >= '%s 00:00:00' and in_date <='%s 24:00:00'" % (sc.date_start,sc.date_end)
		cr.execute(sql % (date, "<>%s"%(sc.location_id.id)))
		res = cr.fetchall()
		if not res or res[0] == 'None':
			return

		for beg in res:
			product_id = beg[0]
			sm_uom_id = beg[1]
			qty = beg[2]
			qty, product_uom_id = self.convert_uom_qty(cr, uid, product_id, sm_uom_id, qty, context=context)
			quant_id = beg[5]
			sql2 = "update vit_stock_summary_line set \
						qty_out = %s \
						where stock_summary_id=%s and stock_quant_id = %s" % \
				   (qty, sc.id, quant_id)
			cr.execute(sql2)

	def update_balance(self, cr, uid, sc, context=None):
		sql3 = "update vit_stock_summary_line set \
			qty_balance =  coalesce( qty_start,0) +  coalesce(qty_in,0) -  coalesce(qty_out,0) \
	    	where stock_summary_id = %s " % (sc.id)
		cr.execute(sql3)

	def beginning_lines_nosn(self, cr, uid, stock_summary_line, sc, context=None):
		date = "date < '%s 24:00:00'" % (sc.date_start)
		line_type = "beg"
		self.process_lines_nosn(cr, uid, line_type, date, stock_summary_line, sc, context=context)



	def mutasi_lines_nosn(self, cr, uid, stock_summary_line, sc, context=None):
		date = "date >= '%s 00:00:00' and date <= '%s 24:00:00'" % (sc.date_start, sc.date_end)
		line_type = "mut"
		self.process_lines_nosn(cr, uid, line_type, date,  stock_summary_line, sc, context=context)


	def process_lines_nosn(self,cr, uid,line_type, date,  stock_summary_line, sc, context=None):

		sql = "select product_id,\
					product_uom,\
					sum(product_uom_qty) \
					from stock_move as m \
					where %s and %s = %s \
					and state = 'done' \
					group by product_id,product_uom \
					order by product_id"

		# incoming
		cr.execute(sql % (date, "location_dest_id", sc.location_id.id))
		res = cr.fetchall()
		if not res or res[0] == 'None':
			return

		if line_type=="beg":
			for beg in res:
				product_id = beg[0]
				sm_uom_id = beg[1]
				qty = beg[2]
				qty,product_uom_id = self.convert_uom_qty(cr, uid, product_id,sm_uom_id,qty,context=context )
				data = {
					"stock_summary_id"	: sc.id,
					"product_id"		: product_id,
					"product_uom_id"	: product_uom_id,
					"qty_start"			: qty,
					"qty_in"			: 0,
					"qty_out"			: 0,
					"qty_balance"		: 0,
				}
				stock_summary_line.create(cr, uid, data, context=context)
		else:
			for incoming in res:
				product_id = incoming[0]
				sm_uom_id = incoming[1]
				qty = incoming[2]
				qty,product_uom_id = self.convert_uom_qty(cr, uid, product_id,sm_uom_id,qty,context=context )

				sql2 = "update vit_stock_summary_line set \
		    	    				qty_in = %s \
		    	    				where stock_summary_id = %s and product_id=%s" % (qty, sc.id, product_id)
				cr.execute(sql2)


		# outgoing
		cr.execute(sql % (date, "location_id", sc.location_id.id))
		res = cr.fetchall()
		if not res or res[0] == 'None':
			return

		if line_type=="beg":
			for beg in res:
				product_id = beg[0]
				sm_uom_id = beg[1]
				qty = beg[2]
				qty,product_uom_id = self.convert_uom_qty(cr, uid, product_id,sm_uom_id,qty,context=context )
				sql2 = "update vit_stock_summary_line set \
							qty_start = qty_start - %s \
							where stock_summary_id = %s and product_id=%s" % (
					qty, sc.id ,product_id )
				cr.execute(sql2)
		else:
			for outgoing in res:
				product_id = outgoing[0]
				sm_uom_id = outgoing[1]
				qty = abs(outgoing[2])
				qty,product_uom_id = self.convert_uom_qty(cr, uid, product_id,sm_uom_id,qty,context=context )

				sql2 = "update vit_stock_summary_line set \
							qty_out = %s \
							where stock_summary_id = %s and product_id=%s" % (
					qty, sc.id, product_id)
				cr.execute(sql2)

		# balance
		sql = "update vit_stock_summary_line set qty_balance = qty_start + qty_in - qty_out \
			where stock_summary_id = %s " % (sc.id)
		cr.execute(sql)

	def convert_uom_qty(self, cr, uid, product_id,sm_uom_id,qty,context=None):

		product = self.pool.get('product.product').browse(cr, uid, product_id, context=context)
		uom 	= self.pool.get('product.uom').browse(cr, uid, sm_uom_id, context=context)

		if product_id == 45:
			print 'ini'
		if uom.id != product.uom_id.id:
			factor = product.uom_id.factor / uom.factor
		else:
			factor = 1.0

		converted_qty = qty * factor

		return converted_qty, product.uom_id.id

	#
	# def beginning_lines_sn(self, cr, uid, stock_summary_line, sc, context=None):
	#
	# 	date = "in_date < '%s'" % (sc.date_start)
	#
	# 	sql = "select product_id,\
	#     		uom_id,\
	#     		lot_id, \
	#     		qty \
	#     		from stock_quant as q \
	#     	  	where %s and location_id = %s \
	#     		order by product_id" % (
	# 		date, sc.location_id.id)
	# 	cr.execute(sql)
	#
	# 	res = cr.fetchall()
	# 	if not res or res[0] == 'None':
	# 		return
	#
	# 	old_product_id = False
	# 	i = 0
	# 	total_start = 0.0
	#
	# 	for beg in res:
	# 		product_id = beg[0]
	#
	#
	# 		### sub total produc
	# 		if old_product_id != product_id and i != 0:
	# 			data = {
	# 				"name"				: "Sub Total %s" % (product_id),
	# 				"stock_summary_id"	: sc.id,
	# 				"product_id"		: False,
	# 				"product_uom_id"	: False,
	# 				"lot_id"			: False,
	# 				"qty_start"			: total_start,
	# 				"qty_in"			: 0,
	# 				"qty_out"			: 0,
	# 				"qty_balance"		: 0,
	# 			}
	# 			stock_summary_line.create(cr, uid, data, context=context)
	# 			total_start = 0.0
	#
	# 		data = {
	# 			"stock_summary_id"	: sc.id,
	# 			"product_id"		: product_id,
	# 			"product_uom_id"	: beg[1],
	# 			"lot_id"			: beg[2],
	# 			"qty_start"			: beg[3],
	# 			"qty_in"			: 0,
	# 			"qty_out"			: 0,
	# 			"qty_balance"		: 0,
	# 		}
	# 		stock_summary_line.create(cr, uid, data, context=context)
	# 		old_product_id = product_id
	# 		total_start += beg[3]
	# 		i += 1
	#
	# def mutasi_lines_sn(self, cr, uid, stock_summary_line, sc, context=None):
	# 	date = "in_date >= '%s' and in_date <= '%s'" % (sc.date_start, sc.date_end)
	#
	# 	sql = "select product_id,\
	#     		uom_id,\
	#     		lot_id, \
	#     		qty \
	#     		from stock_quant as q \
	#     	  	where %s and location_id = %s \
	#     		order by product_id" % (
	# 		date, sc.location_id.id)
	# 	cr.execute(sql)
	#
	# 	res = cr.fetchall()
	# 	if not res or res[0] == 'None':
	# 		return
	#
	# 	for mut in res:
	# 		product_id = mut[0]
	# 		qty_out = 0.0
	# 		qty_in = 0.0
	# 		if mut[3] < 0:
	# 			qty_out = abs(mut[3])
	# 		else:
	# 			qty_in = mut[3]
	#
	# 		data = {
	# 			"qty_in"		: qty_in,
	# 			"qty_out"		: qty_out,
	# 			"qty_balance"	: 0,
	# 		}
	# 		# line
	# 		sql = "update vit_stock_summary_line set \
	# 			qty_in = %s, qty_out = %s, qty_balance = %s \
	# 			where product_id = %s and stock_summary_id=%s" %(qty_in,qty_out,0,product_id,sc.id)
	# 		cr.execute(sql)
	#
	# 		#subtotal
	# 		sql = "update vit_stock_summary_line set qty_in"
	#

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
	_order 		= "product_id"
	_columns 	= {
		"name"			: fields.char("Description"),
		"stock_summary_id"	: fields.many2one('vit.stock_summary_id', 'Stock Card'),
		"stock_quant_id"	: fields.many2one('stock.quant', 'Quant'),
		"product_id"	: fields.many2one('product.product', 'Product'),
		"product_uom_id": fields.many2one('product.uom', 'UoM'),
		"lot_id"		: fields.many2one('stock.production.lot', 'Serial Number'),
		"stock_move_id"	: fields.many2one('stock.move', 'Stock Move'),
		"expired_date"	: fields.related('lot_id','life_date', type='date',
							relation='stock.production.lot',
							string='ED',
							store=True),
		"qty_start"		: fields.float("Start", digits_compute=dp.get_precision('Product Unit of Measure')),
		"qty_in"		: fields.float("Qty In", digits_compute=dp.get_precision('Product Unit of Measure')),
		"qty_out"		: fields.float("Qty Out", digits_compute=dp.get_precision('Product Unit of Measure')),
		"qty_balance"	: fields.float("Balance", digits_compute=dp.get_precision('Product Unit of Measure')),
	}

