{
	"name": "Coba Buat Addons SO",
	"version": "1.0", 
	"depends": [
		"sale"
	],
	"author": "akhmad.daniel@gmail.com", 
	"category": "Education", 
	'website': 'http://www.vitraining.com',
	"description": """\

Manage
======================================================================

Coba menambah field di SO dan menampilkan di form view dan tree
 

""",
	"data": [
		#"security/groups.xml",
		#"menu.xml",
		#"view/web_asset.xml",
		#"data/ir_sequence.xml",
		"view/sale.xml"
	],
	"installable": True,
	"auto_install": False,
    "application": True,
}