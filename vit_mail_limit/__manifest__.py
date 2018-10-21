{
	"name": "Mail Sending Limit",
	"version": "1.0", 
	"depends": [
		"mail",
		"mass_mailing",
	],
	"author": "Akhmad D. Sembiring [vitraining.com]",
	"category": "Marketing",
	'website': 'http://www.vitraining.com',
	"description": """
Add System Parameter/ mail.send_limit eg 100 per hour.
Inherit mail.process_email_queue() to apply that limit to send email to SMTP provider


            Find our other interesting modules that can make your life easier:
            https://www.odoo.com/apps/modules/browse?search=vitraining
""",
	"data": [
		"parameters.xml"
	],
	"installable": True,
	"auto_install": False,
    "application": False,
}