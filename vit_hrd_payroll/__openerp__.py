{
	"name": "HRD Payroll Indonesian Companies",
	"version": "1.0", 
	"depends": ["base","board"], 
	"author": "Vitraining", 
	"category": "HRD", 
	"description": """\
this is payroll system module for Indonesian Companies
""",
	"depends" : [
		'hr_contract',
		'hr_payroll'],
	"data": [
		"contract_view.xml",
		"salary_structure.xml",
		"payslip_report.xml",
		"payroll_view.xml",
		"pkp.xml",
		"data/hr.pkp.csv",
		"data/hr.ptkp.csv",
	],
	"installable": False,
	"auto_install": False,
	"application": True,
}