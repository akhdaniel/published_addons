from openerp import tools
from openerp.osv import fields,osv
import openerp.addons.decimal_precision as dp
import time
import logging
from openerp.tools.translate import _

_logger = logging.getLogger(__name__)
CASHFLOW_STATES =[('draft','Draft'),('open','Verifikasi'), ('reject','Ditolak'),
                 ('done','Disetujui')]


class cashflow_coa(osv.osv):
	_name 		= 'anggaran.cashflow.coa'
	_columns = {
		'code'		: fields.char('Code'),
		'parent_id'	: fields.many2one('anggaran.cashflow.coa', 'Parent'),
		'name'		: fields.char('Name')
	}

class cashflow(osv.osv):
	_name 		= 'anggaran.cashflow'
	_columns = {
		'name'				: fields.char('No'),
		'tanggal'			: fields.date('Tanggal'),
		'fakultas_id'		: fields.many2one('anggaran.fakultas', 'Fakultas'),
		'jurusan_id'		: fields.many2one('anggaran.jurusan', 'Jurusan'),
		'unit_id'			: fields.many2one('anggaran.unit', _('Unit Kerja'), required=True),
		'tahun_id'			: fields.many2one('account.fiscalyear', 'Tahun', required=True),
		'cashflow_line_ids'	: fields.one2many('anggaran.cashflow.line','cashflow_id','Lines', ondelete="cascade"),
		'state'             : fields.selection(CASHFLOW_STATES,'Status',readonly=True,required=True),
		'user_id'			: fields.many2one('res.users', 'Create By'),
		'show_actual'		: fields.boolean('Show Actual'),
		'show_deviasi'		: fields.boolean('Show Deviation'),
		'revision'			: fields.integer('Revision'),
	}
	_defaults = {
		'state'       	: CASHFLOW_STATES[0][0],
		'tanggal'     	: lambda *a : time.strftime("%Y-%m-%d") ,
		'user_id'		: lambda obj, cr, uid, context: uid,
		'name'			: lambda obj, cr, uid, context: '/',	
		'show_actual'	: True,
		'show_deviasi'	: True,
	}
	def action_draft(self,cr,uid,ids,context=None):
		#set to "draft" state
		return self.write(cr,uid,ids,{'state':CASHFLOW_STATES[0][0]},context=context)
	
	def action_confirm(self,cr,uid,ids,context=None):
		#set to "confirmed" state
		return self.write(cr,uid,ids,{'state':CASHFLOW_STATES[1][0]},context=context)
	
	def action_reject(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':CASHFLOW_STATES[2][0]},context=context)
	
	def action_done(self,cr,uid,ids,context=None):
		#set to "done" state
		return self.write(cr,uid,ids,{'state':CASHFLOW_STATES[3][0]},context=context)

	def create(self, cr, uid, vals, context=None):
		if context is None:
			context = {}
		if vals.get('name', '/') == '/':
			vals['name'] = self.pool.get('ir.sequence').get(cr, uid, 'anggaran.cashflow') or '/'
		new_id = super(cashflow, self).create(cr, uid, vals, context=context)
		return new_id

	def action_recalculate(self,cr,uid,ids,context=None):
		divider = 1000

		cr.execute('delete from anggaran_cashflow_line where cashflow_id=%s' % ids[0] )

		cf = self.browse(cr, uid, ids[0], context=context)
		coa_obj = self.pool.get('anggaran.cashflow.coa')
		line_obj = self.pool.get('anggaran.cashflow.line')

		coa_ids = coa_obj.search(cr, uid, [], context=context)

		p_line_ids = {}
		a_line_ids = {}
		v_line_ids = {}

		saldo_akhir = {}

		for m in range(1,13):

			p_total_income = 0.0
			p_total_biaya_unit = 0.0
			p_total_biaya_adm = 0.0
			p_total_pengeluaran = 0.0
			p_total_pendanaan = 0.0


			for coa in coa_obj.browse(cr, uid, coa_ids, context=context):

				p_mfield = 0
				a_mfield = 0
				v_mfield = 0

				if coa.code == '1':
					p_mfield = saldo_akhir.get(m-1, 0)
					saldo_awal = saldo_akhir.get(m-1, 0)
				
				if coa.code == '2.1':
					if (m in range(1,5)) or (m in range(7,11)) :
						p_mfield = self.cari_bpp_mhs(cr, uid, cf)/4
					p_total_income += p_mfield 

				if coa.code == '2.2':
					if m == 1:
						p_mfield = self.cari_spp_mhs(cr, uid, cf) 
					p_total_income += p_mfield

				if coa.code == '2.3':
					p_mfield = self.cari_tagihan_lain(cr, uid, cf)
					p_total_income += p_mfield

				if coa.code == '2.4':
					p_mfield = self.cari_income_lain(cr, uid, cf)
					p_total_income += p_mfield

				if coa.code == '2.100':
					p_mfield = saldo_awal+ p_total_income


				if coa.code == '3.1':
					hasil = self.cari_bahan_habis_pakai(cr, uid, cf, m)
					p_mfield = hasil[0]
					a_mfield = hasil[1]
					v_mfield = hasil[2]
					p_total_biaya_unit += p_mfield

				if coa.code == '3.2':
					hasil = self.cari_gaji(cr, uid, cf, m)
					p_mfield = hasil[0]
					a_mfield = hasil[1]
					v_mfield = hasil[2]
					p_total_biaya_unit += p_mfield

				if coa.code == '3.3':
					hasil = self.cari_sewa(cr, uid, cf, m)
					p_mfield = hasil[0]
					a_mfield = hasil[1]
					v_mfield = hasil[2]
					p_total_biaya_unit += p_mfield

				if coa.code == '3.4':
					hasil = self.cari_outsourcing(cr, uid, cf, m)
					p_mfield = hasil[0]
					a_mfield = hasil[1]
					v_mfield = hasil[2]
					p_total_biaya_unit += p_mfield

				if coa.code == '3.5':
					hasil = self.cari_overhead(cr, uid, cf, m)
					p_mfield = hasil[0]
					a_mfield = hasil[1]
					v_mfield = hasil[2]
					p_total_biaya_unit += p_mfield

				if coa.code == '3.100':
					p_mfield = p_total_biaya_unit 


				if coa.code == '3.6':
					p_mfield = self.cari_biaya_adm(cr, uid, cf, m)
					p_total_pengeluaran += p_mfield

				if coa.code == '3.7':
					hasil = self.cari_investasi(cr, uid, cf, m)
					p_mfield = hasil[0]
					a_mfield = hasil[1]
					v_mfield = hasil[2]
					p_total_pengeluaran += p_mfield

				if coa.code == '3.8':
					p_mfield = self.cari_biaya_prepaid(cr, uid, cf, m)
					p_total_pengeluaran += p_mfield

				if coa.code == '3.9':
					p_mfield = self.cari_pajak(cr, uid, cf,m)
					p_total_pengeluaran += p_mfield

				if coa.code == '3.10':
					hasil = self.cari_uudp(cr, uid, cf, m)
					p_mfield = hasil[0]
					a_mfield = hasil[1]
					v_mfield = hasil[2]
					p_total_pengeluaran += p_mfield

				if coa.code == '3.11':
					p_mfield = self.cari_saving(cr, uid, cf,m)
					p_total_pengeluaran += p_mfield

				if coa.code == '3.200':
					p_mfield = p_total_pengeluaran

				if coa.code == '3.300':
					p_mfield = saldo_awal + p_total_income - p_total_biaya_unit - p_total_pengeluaran


				if coa.code == '4.1':
					p_mfield = self.cari_pinjaman(cr, uid, cf,m)
					p_total_pendanaan += p_mfield

				if coa.code == '4.2':
					p_mfield = self.cari_pembayaran_pinjaman(cr, uid, cf,m)
					p_total_pendanaan += p_mfield

				if coa.code == '4.3':
					p_mfield = self.cari_bunga_pinjaman(cr, uid, cf,m)
					p_total_pendanaan += p_mfield

				if coa.code == '4.100':
					p_mfield = p_total_pendanaan 

				if coa.code == '5':
					p_mfield =  saldo_awal + p_total_income - p_total_biaya_unit - p_total_pengeluaran + p_total_pendanaan
					saldo_akhir[m] = p_mfield


				p_data = {
					'cashflow_id' : cf.id ,
					'cashflow_coa_id'	: coa.id,
					'type' : 'p',
					('m%s' % m) : p_mfield / divider,
				}
				a_data = {
					'cashflow_id' : cf.id ,
					# 'cashflow_coa_id'	: coa.id,
					'type' : 'a',
					('m%s' % m) : a_mfield / divider,
				}

				v_data = {
					'cashflow_id' : cf.id ,
					# 'cashflow_coa_id'	: coa.id,
					'type' : 'v',
					('m%s' % m) : v_mfield / divider,
				}

				if m == 1:
					p_line_id = line_obj.create(cr, uid, p_data , context=context)
					p_line_ids.update({ coa.id: p_line_id })

					if cf.show_actual:
						a_line_id = line_obj.create(cr, uid, a_data , context=context)
						a_line_ids.update({ coa.id: a_line_id })
					if cf.show_deviasi:
						v_line_id = line_obj.create(cr, uid, v_data , context=context)
						v_line_ids.update({ coa.id: v_line_id })

				else:
					line_obj.write(cr, uid, p_line_ids[ coa.id ], p_data, context=context)
					if cf.show_actual:
						line_obj.write(cr, uid, a_line_ids[ coa.id ], a_data, context=context)
					if cf.show_deviasi:
						line_obj.write(cr, uid, v_line_ids[ coa.id ], v_data, context=context)


		self.write(cr, uid, ids, {'revision':cf.revision+1}, context=context)
		return

	#cari dari jurusan_income total record total
	def cari_spp_mhs(self, cr, uid, cf):
		jurusan_id = cf.jurusan_id
		total = 0.0
		for inc in jurusan_id.income_ids:
			total += inc.total_spp
		return total 

	def cari_bpp_mhs(self, cr, uid, cf):
		jurusan_id = cf.jurusan_id
		total = 0.0
		for inc in jurusan_id.income_ids:
			total += inc.total_bpp
		return total 

	def cari_income_lain(self, cr, uid, cf):
		total = 0.0
		return total

	def cari_tagihan_lain(self, cr, uid, cf):
		total = 0.0
		return total 

	def query_rka_coa(self, cr, uid, cf, cost_type_code , m):
		total_p = 0.0
		total_a = 0.0
		total_v = 0.0

		tahun = int(cf.tahun_id.code)
		tahun,m = self.map_month_to_period(cr, uid, m, tahun )

		sql = "SELECT sum(rka_coa.total), sum(rka_coa.realisasi), sum(rka_coa.total)-sum(coalesce(rka_coa.realisasi,0)) "
		sql += "FROM anggaran_rka rka "
		sql += "LEFT JOIN account_period per ON rka.period_id = per.id "
		sql += "LEFT JOIN anggaran_rka_kegiatan rka_keg ON rka.id = rka_keg.rka_id "
		sql += "LEFT JOIN anggaran_rka_coa rka_coa ON rka_keg.id = rka_coa.rka_kegiatan_id "
		sql += "LEFT JOIN anggaran_mata_anggaran_kegiatan mak ON rka_coa.mak_id = mak.id "
		sql += "LEFT JOIN anggaran_cost_type ct ON mak.cost_type_id = ct.id "
		sql += "WHERE rka.unit_id = %s " % (cf.unit_id.id)
		sql += "AND rka.tahun = %s " % (cf.tahun_id.id)
		sql += "AND ct.code = '%s' " % (cost_type_code)
		sql += "AND rka.state = 'done' "
		sql += "AND per.code = '%02d/%s' " % ( m, tahun) 
		
		cr.execute(sql)
		hasil = cr.fetchone()

		print sql
		print hasil

		if hasil[0] != None:
			total_p = hasil[0]

		if hasil[1] != None:
			total_a = hasil[1]

		if hasil[2] != None:
			total_v = hasil[2]
			
		return (total_p, total_a, total_v)


	def cari_bahan_habis_pakai(self, cr, uid, cf, m):
		total = self.query_rka_coa(cr, uid, cf, "1",m)
		return total 

	def cari_gaji(self, cr, uid, cf,m):
		total = self.query_rka_coa(cr, uid, cf, "2",m)
		return total 

	def cari_sewa(self, cr, uid, cf,m):
		total = self.query_rka_coa(cr, uid, cf, "3",m)
		return total 

	def cari_outsourcing(self, cr, uid, cf,m):
		total = self.query_rka_coa(cr, uid, cf, "4",m)
		return total 

	def cari_overhead(self, cr, uid, cf,m):
		total = self.query_rka_coa(cr, uid, cf, "5",m)
		return total 

	def cari_biaya_adm(self, cr, uid, cf, m):
		total = 0.0
		return total 

	def map_month_to_period(self, cr, uid, m, tahun):
		m = m + 8
		if m > 12:
			m = m - 12
			tahun = tahun + 1

		return tahun, m

	def cari_investasi(self, cr, uid, cf, m):
		# m : 1=Sep, 2=Oct, dst..
		# period : 01=Jan, 02=Feb
		tahun = int(cf.tahun_id.code)

		tahun,m = self.map_month_to_period(cr, uid, m, tahun )

		p_total = 0.0
		a_total = 0.0
		v_total = 0.0

		sql = "SELECT sum(total),0,0 from anggaran_investasi inv "
		sql += "LEFT JOIN account_period per ON inv.period_id = per.id "
		sql += "WHERE unit_id = %s " % (cf.unit_id.id)
		sql += "AND tahun_id = %s " % (cf.tahun_id.id) 
		sql += "AND per.code = '%02d/%s' " % ( m, tahun) 
		sql += "AND inv.state = 'done'"


		cr.execute(sql)
		hasil = cr.fetchone()

		# print sql 
		# print hasil

		if hasil[0] != None:
			p_total = hasil[0]
		if hasil[1] != None:
			a_total = hasil[1]
		if hasil[2] != None:
			v_total = hasil[2]
		return (p_total, a_total, v_total)

	def cari_biaya_prepaid(self, cr, uid, cf, m):
		total = 0.0
		return total 

	def cari_pajak(self, cr, uid, cf,m):
		total = 0.0
		return total 

	def cari_uudp(self, cr, uid, cf, m):
		# m : 1=Sep, 2=Oct, dst..
		# period : 01=Jan, 02=Feb
		tahun = int(cf.tahun_id.code)

		tahun,m = self.map_month_to_period(cr, uid, m, tahun )
		
		p_total = 0.0
		a_total = 0.0
		v_total = 0.0

		sql = "SELECT sum(jumlah),0,0 from anggaran_sup sup "
		sql += "LEFT JOIN account_period per ON sup.period_id = per.id "
		sql += "WHERE unit_id = %s " % (cf.unit_id.id)
		sql += "AND tahun_id = %s " % (cf.tahun_id.id) 
		sql += "AND per.code = '%02d/%s' " % ( m, tahun) 
		sql += "AND sup.state = 'done'"


		cr.execute(sql)
		hasil = cr.fetchone()

		# print sql 
		# print hasil

		if hasil[0] != None:
			p_total = hasil[0]
		if hasil[1] != None:
			a_total = hasil[1]
		if hasil[2] != None:
			v_total = hasil[2]

		return (p_total, a_total, v_total)

	def cari_saving(self, cr, uid, cf,m):
		total = 0.0
		return total 

	def cari_pinjaman(self, cr, uid, cf,m):
		total = 0.0
		return total 

	def cari_pembayaran_pinjaman(self, cr, uid, cf,m):
		total = 0.0
		return total 

	def cari_bunga_pinjaman(self, cr, uid, cf,m):
		total = 0.0
		return total 



class cashflow_line(osv.osv):
	_name 		= 'anggaran.cashflow.line'
	_columns = {
		'cashflow_id': fields.many2one('anggaran.cashflow', 'Cashflow'),
		'cashflow_coa_id': fields.many2one('anggaran.cashflow.coa', 'Rincian'),
		'code': fields.related('cashflow_coa_id', 'code' , type="char", relation="anggaran.cashflow_coa", string="Code", store=False),
		'type': fields.char('Type'),
		'm1' : fields.float('Sep'),
		'm2' : fields.float('Oct'),
		'm3' : fields.float('Nov'),
		'm4' : fields.float('Dec'),
		'm5' : fields.float('Jan'),
		'm6' : fields.float('Feb'),
		'm7' : fields.float('Mar'),
		'm8' : fields.float('Apr'),
		'm9' : fields.float('May'),
		'm10' : fields.float('Jun'),
		'm11' : fields.float('Jul'),
		'm12' : fields.float('Aug'),

		'm1a' : fields.float('Sep (a)'),
		'm2a' : fields.float('Oct (a)'),
		'm3a' : fields.float('Nov (a)'),
		'm4a' : fields.float('Dec (a)'),
		'm5a' : fields.float('Jan (a)'),
		'm6a' : fields.float('Feb (a)'),
		'm7a' : fields.float('Mar (a)'),
		'm8a' : fields.float('Apr (a)'),
		'm9a' : fields.float('May (a)'),
		'm10a' : fields.float('Jun (a)'),
		'm11a' : fields.float('Jul (a)'),
		'm12a' : fields.float('Aug (a)'),

		'm1s' : fields.float('Sep (s)'),
		'm2s' : fields.float('Oct (s)'),
		'm3s' : fields.float('Nov (s)'),
		'm4s' : fields.float('Dec (s)'),
		'm5s' : fields.float('Jan (s)'),
		'm6s' : fields.float('Feb (s)'),
		'm7s' : fields.float('Mar (s)'),
		'm8s' : fields.float('Apr (s)'),
		'm9s' : fields.float('May (s)'),
		'm10s' : fields.float('Jun (s)'),
		'm11s' : fields.float('Jul (s)'),
		'm12s' : fields.float('Aug (s)'),				

	}
