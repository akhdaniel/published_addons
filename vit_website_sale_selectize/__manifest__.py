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