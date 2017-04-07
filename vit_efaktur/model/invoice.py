from openerp import api, fields, models


class invoice(models.Model):
	_name = 'account.invoice'
	_inherit = 'account.invoice'


	efaktur_id = fields.Many2one(
		comodel_name="vit.efaktur",
		string="Nomor eFaktur"
	)
	
	
	def export_efaktur(self):
		data = {
			"A" : "FK",
			"B" : "KD_JENIS_TRANSAKSI",
			"C" : "FG_PENGGANTI",
			"D" : "NOMOR_FAKTUR",
			"E" : "MASA_PAJAK",
			"F" : "TAHUN_PAJAK",
			"G" : "TANGGAL_FAKTUR",
			"H" : "NPWP",
			"I" : "NAMA",
			"J" : "ALAMAT_LENGKAP",
			"K" : "JUMLAH_DPP",
			"L" : "JUMLAH_PPN",
			"M" : "JUMLAH_PPNBM",
			"N" : "ID_KETERANGAN_TAMBAHAN",
			"O" : "FG_UANG_MUKA",
			"P" : "UANG_MUKA_DPP",
			"Q" : "UANG_MUKA_PPN",
			"R" : "UANG_MUKA_PPNBM",
			"S" : "REFERENSI"
		}
		self.env['vit.faktur'].create(data)
		data = {
			"A" : "LT",
			"B" : "NPWP",
			"C" : "NAMA",
			"D" : "JALAN",
			"E" : "BLOK",
			"F" : "NOMOR",
			"G" : "RT",
			"H" : "RW",
			"I" : "KECAMATAN",
			"J" : "KELURAHAN",
			"K" : "KABUPATEN",
			"L" : "PROPINSI",
			"M" : "KODE_POS",
			"N" : "NOMOR_TELEPON",
		}

		self.env['vit.faktur'].create(data)

		for invoice in self:
			data = {
				'A': invoice.number ,
				'B': invoice.amount_total ,
				'C':'',
				'D':'',
				'E':'',
				'F':'',
				'G':'',
				'H':'',
				'I':'',
				'J':'',
				'K':'',
				'L':'',
				'M':'',
				'N':'',
				'O':'',
				'P':'',
				'Q':'',
				'R':'',
				'S':'koloms',
			}
			self.env['vit.faktur'].create(data)

		return
	
