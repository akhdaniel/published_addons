import time
from openerp.report import report_sxw 

class payslip_report(report_sxw.rml_parse): 
    def __init__(self, cr, uid, name, context): 
        super(payslip_report, self).__init__(cr, uid, name, context) 
        self.localcontext.update({ 'time': time, }) 
        
report_sxw.report_sxw('report.payslip_report', 'hr.payslip', 'addons/hrd_payroll/report/payslip_bijb.rml', parser=payslip_report) 