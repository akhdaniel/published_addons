{
	"name": "Menambahkan eFaktur",
	"version": "1.0", 
	"depends": [
		"account",
	],
	"author": "agungarisandi4@gmail.com",
	"website": "vitraining.com",
	"category": "Accounting",
	"description": """\

Manage
======================================================================

* Menambahkan master nomor eFaktur di menu accounting
* Generate nomor efaktur via wizard (start to end)
* Menambahkan field NPWP di Customer / res.partner
* Me-link nomor efaktur ke Invoice , batasan hanya yang belum dipakai ynag bisa muncul
* Export data Customer, Barang, Invoice ke format CSV efaktur


""",
	"data": [
		"wizard/generate.xml",
		"view/efaktur.xml",
		"view/partner.xml",
		"view/invoice.xml",
	],
	"installable": True,
	"application": True,
	"auto_install": False,
}