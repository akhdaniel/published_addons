{
    'version': '2.2',
    'name': 'Aplikasi Anggaran Universitas',
    'depends': ['base','account','product', 'hr','report'],
    'author'  :'vitraining.com',
    'category': 'Accounting',
    'data': [
        'menu/menu_master.xml',
    	'menu/menu_anggaran.xml',
        'menu/menu_transaksi.xml',
    	#'menu/menu_laporan.xml',
        # #'data/data_ir_sequence.xml',
      

        'data/sample/anggaran.fakultas.csv',
        'data/sample/anggaran.jurusan.csv',
        'data/sample/anggaran.unit.csv',

        'data/sample/anggaran.tridharma.csv',
        'data/sample/anggaran.cost_type.csv',
        'data/sample/anggaran.sumber_dana.csv',
        'data/sample/anggaran.category.csv',
        'data/sample/anggaran.kebijakan.csv',
        'data/sample/anggaran.program.csv',
        'data/sample/anggaran.kegiatan.csv',
        'data/sample/anggaran.mata_anggaran_kegiatan.csv',

        'view/kebijakan.xml',
    	'view/program.xml',
    	'view/kegiatan.xml',
        'view/mata_anggaran_kegiatan.xml',
        'view/cost_type.xml',
        'view/tridharma.xml',
        'view/fakultas.xml',
    	'view/jurusan.xml',
    	'view/unit.xml',

        'view/rka.xml',
        'view/rka_detail.xml',

        'view/sup.xml',


    	#'view/tup.xml',
      #'view/spp.xml',
      #'view/sptb.xml',
      #'view/spm.xml',
      #'view/kas.xml',
      #'view/biaya.xml',

      #'view/cashflow.xml',
      #'view/investasi.xml',

      #'view/lap_pdana.xml',
    	#'view/lap_pkk.xml',
      
      #'report/spm.xml',
      ##'report/paper.xml',
      #'report/rka.xml',
      #'report/cashflow.xml',

      #'security/groups.xml',
      #'security/ir.model.access.csv'
    ],    
    'description': """
Description
==================
Aplikasi untuk mencatat anggaran, penggunaan, dan pertanggungjawaban.
Laporan yang dihasilkan; anggaran, realisasi, dan sisa anggaran.

Model
====================

Transaksi 

rka        : hedaer RAK 
               tahun, belongs to Fakultas 
rka_kegiatan   : detail rencana kegiatan dan anggaran
               belongs to rka, 
               related kebijakan, 
               related program, 
               belongs to kegiatan, 
               belongs to coa , 
               belongs to detail angka 
rka_coa
rka_detail
rka_volume

sup           : surat pengajuan uang persediaan   

a_spp        : surat Permintaan Pembayaran
a_spp_line   : detail spp many2one a_rak_line 

a_sptb       : Surat Pernyataan Tanggung Jawab Belanja
               many2one a_rak_line 
               hasmany partners 
a_sptb_line  : detail sptb
               many2one partner atau many2one a_cash (disini ada partner)

a_spm        : Surat Perintah Membayar
a_spm_line   : detail spm 
               many2one a_rak_line 

a_cash       : Transaksi Kas Masuk dan Kas Keluar

Master data 

a_coa        : chart of account sistem Akuntansi
a_kebijakan  : Kebijakan
a_program    : Program 
a_kegiatan   : mata anggaran kegiatan
a_coa_sap    : COA Sistem Akuntansi Pemerintahan (SAP)
a_sumber     : Sumber Dana
a_fakultas   : Fakultas
a_jurusan    : Jurusan dan Prodi (belongs to a_fakultas)
a_unit_kerja : Unit Kerja 

Menu Sistem Anggaran 
====================

Anggaran
	Rincian Kegiatan dan Anggaran
	Monitoring Budget dan Realisasi (report)
	Pencapaian Kinerja Kegiatan

Realisasi 
	Surat Pengajuan Uang Persediaan
		Surat Pernyataan Penggunaan Dana TUP (print out)
	Surat Permintaan Pembayaran
	Surat Pernyataan Tanggung Jawab Belanja
		Surat Penolakan (print out)
		Surat Rekomendasi (print out)
	Surat Perintah Membayar
		Surat Perintah Transfer Rekening (print out)
	
Akuntansi dan Keuangan 
	Surat Permintaan Pengeluaran Kas Kecil
	Transaksi Kas Masuk dan Kas Keluar
	Laporan Penggunaan Dana
	Laporan Kas Kecil
	Buku Kas Umum
	Buku Pembantu Kas Tunai
	Laporan Keuangan per Periode (Neraca, Rugi Laba, Cash Flow)
	Pencetakan Bukti Potong PPH21,23 

Aktiva Tetap 
	Proses dan SOP pencatatan Fixed Asset
	Perhitungan Depresiasi
	Jurnal Depresiasi
	Import Fixed Asset
	Export Data SIMAK BMN

Master Data 
	Kebijakan 
	Program (belongs to Kebijakan)
	Kegiatan (belongs to Program)

	Chart of Account (COA)
	COA Sistem Akuntansi Pemerintahan (SAP)
		Konversi MAK vs COA
	
	Sumber Dana
	Satuan (link ke uom)
	Fakultas
	Jurusan dan Prodi 
	Unit Kerja


Journal yang terbentuk
=======================

Pusat: 
---------
1. Pencairan UMK dari Keuangan Pusat 

UMK Fakultas    10
	    Bank Pusat      10


9. pertanggungjawaban Fakultas

RAK Universitas   10
       UMK Fakultas       10



Fakultas:
---------
2. Terima oleh UMK 

Bank Fakultas   10 
        RAK Pusat       10 

3. Penarikan Tunai 

Kas Fakultas    10
        Bank Fakultas   10 

4. Distrbusi oleh UMK 

UMK Prodi/Jurusan   10 
        Kas Fakultas    10 

8. Pengembalian Sisa ke Pusat 

Bank Pusat          2
        Kas Fakultas        2


Prodi/Jurusan:
----------

5. Terima dari Fakultas

Kas Prodi/Jurusan    10
        RAK Fakultas      10

6. Realisasi (misalnya terpakai hanya 8)

Beban-beban            8
        Kas Prodi/Jurusan      8

7. Sisa UMK ke Fakultas

Kas Fakultas           2
         Kas Prodi             2

7. pertanggungjawaban ke Fakultas

RAK Fakultas          10
        UMK Prodi Jurusan      10




""",
    'installable':True,

}
