{
	"name": "Inherit Website Sale Checkout Form",
	"version": "1.0", 
	"depends": [
		"vit_kelurahan",
		"website_sale",
		"stock",
	],
	"author": "akhmad.daniel@gmail.com", 
	"category": "Education", 
	'website': 'http://www.vitraining.com',
	"description": """\
	
Inherit Website Sale Checkout Form using selectize.js cascading select Country - State - City - Kecamatan - Kelurahan


Sample addon accompanying the ebook Integrating Selectize.js with Odoo:
https://play.google.com/store/books/details/Akhmad_D_Sembiring_Panduan_Integrasi_Odoo_v10_deng?id=wAJMDwAAQBAJ


Find our other interesting modules that can make your life easier:
https://www.odoo.com/apps/modules/browse?search=vitraining

    
""",
	"data": [
		"data/whitelist.xml",
		"view/web_asset.xml",
		"view/templates.xml",
	],
	"installable": True,
	"auto_install": False,
    "application": True,
}