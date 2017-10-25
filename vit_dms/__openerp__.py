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

		"data/cron.xml",

		"view/web_asset.xml",

		"data/ir_sequence.xml",
		"data/dms.legal_document_type.csv",
		"data/dms.legal_hasil_penyesuaian.csv",
		"data/dms.legal_region.csv",
		"data/dms.legal_status_bisnis_grade.csv",
		"data/dms.legal_status_grade.csv",

		"data/dms.classification.csv",
		"data/dms.document_type.csv",

		"data/email.xml",

		"view/document.xml",
		"view/document_type.xml",
		"view/legal_document_type.xml",
		"view/legal_region.xml",
		"view/legal_status_grade.xml",
		"view/legal_branch.xml",
		"view/legal.xml",
		"view/legal_rule.xml",
		"view/template.xml",
	],
	"installable": True,
	"auto_install": False,
    "application": True,
}