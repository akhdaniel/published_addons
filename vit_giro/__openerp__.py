{
	"name": "Giro",
	"version": "1.1",
	"depends": [
		"account"
	], 
	"author": "akhmad.daniel@gmail.com", 
	"category": "Accounting",
	"website": 'http://www.vitraining.com',
	"description": """\

Features
======================================================================

* mencatat data cek dan giro yg dikeluarkan atau diterima perusahaan untuk membayar hutang atau pelunasan piutang
* created menu:
	* Accounting / Giro / Giro
* created object
	* vit.giro
* created views
	* giro
	* invoice
* logic:
	* user mencatat giro dan mengalokasikan ke invoice-invoice yg hendak di bayar
	* user bisa lihat daftar giro yg jatuh tempo per hari
	* jika dicek ke rek bank, giro tersebut sdh clearing maka user klik tombol clearing
	* system akan membuat invoice payment sesuai alokasi pada giro


Special thanks to Mr Tiongsin for the business logics :)

""",
	"data": [
		"menu.xml", 
		"view/giro.xml",
		"view/invoice.xml",
	],
	"installable": True,
	"auto_install": False,
	"application": True,
}