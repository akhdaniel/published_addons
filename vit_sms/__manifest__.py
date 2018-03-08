{
	"name": "vitSMS - Base Module",
	"version": "1.3",
	"depends": [
		"base",
		"mail"
	],
	"author": "Akhmad D. Sembiring [vitraining.com]",
	"category": "Extra Tools",
	'website': 'http://www.vitraining.com',
	'images': ['static/description/images/main_screenshot.jpg'],
	'summary': 'Send SMS from Odoo Applications',
	"description": """\

""",
	"data": [
		"security/groups.xml",
		"security/ir.model.access.csv",
		"top_menu.xml",
		"data/ir_sequence.xml",
		"view/outbox.xml",
		"view/group.xml",
		"view/sent.xml",
		"view/config.xml",
		"view/send_sms.xml",
		"data/cron.xml",
		#"wizard/outbox_wizard.xml",
	],
	"installable": True,
	"auto_install": False,
    "application": True,
}