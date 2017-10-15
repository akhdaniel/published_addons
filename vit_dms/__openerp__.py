{
	"name": "Document Management System",
	"version": "1.0", 
	"depends": [
		"mail",
		"hr",
		"muk_dms",
	],
	"author": "Akhmad D. Sembiring [vitraining.com]",
	"category": "Document",
	'website': 'http://www.vitraining.com',
	'images': ['static/description/images/main_screenshot.jpg'],
	'summary': 'Manage documents per Type and Directorate',
	"description": """\

Manage
======================================================================

* this is my academic information system module
* created menu:
* created object
* created views
* logic:

""",
	"data": [
		"security/groups.xml",
		"security/ir.model.access.csv",
		#"top_menu.xml",
		"view/web_asset.xml",
		"data/ir_sequence.xml",
		#"data/hr.department.csv",
		#"data/dms.directorate.csv",
		"data/dms.document_type.csv",
		"view/document.xml",
		"view/document_type.xml",
		#"view/department.xml",
		"view/template.xml",
	],
	"installable": True,
	"auto_install": False,
    "application": True,
}