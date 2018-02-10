import time
import pprint
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta

from openerp import api, tools
from openerp.osv import fields, osv
from openerp.tools.translate import _
import openerp.addons.decimal_precision as dp

from openerp.tools.safe_eval import safe_eval as eval

class hr_payslip(osv.osv):
    '''
    Pay Slip
    '''

    _name = 'hr.payslip'
    _inherit = 'hr.payslip'
    _description = 'Pay Slip'

    def confirm_email(self, cr, uid, ids, context=None):
        '''
        This function opens a window to compose an email, with the edi sale template message loaded by default
        '''
        import pdb;pdb.set_trace()
        assert len(ids) == 1, 'This option should only be used for a single id at a time.'
        ir_model_data = self.pool.get('ir.model.data')
        try:
            template_id = ir_model_data.get_object_reference(cr, uid, 'hrd_payroll', 'email_template_edi_payslip')[1]
        except ValueError:
            template_id = False
        try:
            compose_form_id = ir_model_data.get_object_reference(cr, uid, 'mail', 'email_compose_message_wizard_form')[1]
        except ValueError:
            compose_form_id = False 
        ctx = dict()
        ctx.update({
            'default_model': 'hr.payslip',
            'default_res_id': ids[0],
            'default_use_template': bool(template_id),
            'default_template_id': template_id,
            'default_composition_mode': 'comment',
            'mark_so_as_sent': True
        })
        return {
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'mail.compose.message',
            'views': [(compose_form_id, 'form')],
            'view_id': compose_form_id,
            'target': 'new',
            'context': ctx,
        }
    
    def compute_sheet(self, cr, uid, ids, context=None):
        slip_line_pool = self.pool.get('hr.payslip.line')
        sequence_obj = self.pool.get('ir.sequence')

        tunj_jabatan = 0
        tunj_makan = 0
        tunj_transport = 0
        overtime = 0
        thr = 0
        bonus = 0
        ketidakhadiran = 0
        kasbon = 0
        cicilan = 0
        gross = 0
        net = 0
        zakat = 0
    
        for payslip in self.browse(cr, uid, ids, context=context):
            
            # mencari jumlah izin dan sakit
            line_ids = payslip.worked_days_line_ids
            jum = 0.0
            for IS in line_ids :
                codes = IS.code
                if codes == "IZIN" or codes == "SAKIT" :
                    jum += IS.number_of_days
            self.write(cr,uid,[payslip.id],{'jum_is': jum}) 
            #################

            #################################
            izin = 0 
            hari_kerja = 0
            tk=0
            for hari in payslip.worked_days_line_ids :
                if hari.code == 'WORK100' :
                    hari_kerja = int(hari.number_of_days)
                if hari.code == 'IZIN' :
                    izin = int(hari.number_of_days)
                if hari.code == 'TK' :
                    tk = int(hari.number_of_days)
            self.write(cr,uid,[payslip.id],{"jum_harikerja": hari_kerja,
                                            "jum_harikerja1": hari_kerja , 
                                            "izin":izin,
                                            "tk":tk})
            #################################

            number = payslip.number or sequence_obj.get(cr, uid, 'salary.slip')
            #delete old payslip lines
            old_slipline_ids = slip_line_pool.search(cr, uid, [('slip_id', '=', payslip.id)], context=context)
#            old_slipline_ids
            if old_slipline_ids:
                slip_line_pool.unlink(cr, uid, old_slipline_ids, context=context)
            if payslip.contract_id:
                #set the list of contract for which the rules have to be applied
                contract_ids = [payslip.contract_id.id]
            else:
                #if we don't give the contract, then the rules to apply should be for all current contracts of the employee
                contract_ids = self.get_contract(cr, uid, payslip.employee_id, payslip.date_from, payslip.date_to, context=context)
            lines = [(0,0,line) for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context)]
            self.write(cr, uid, [payslip.id], {'line_ids': lines, 'number': number,}, context=context)     
            for line in self.pool.get('hr.payslip').get_payslip_lines(cr, uid, contract_ids, payslip.id, context=context):
                cod = line["code"]
                if cod == "TJB" :
                    tunj_jabatan = line["amount"]
                if cod == "TJM" :
                    tunj_makan = line["amount"]
                if cod == "TJT" :
                    tunj_transport = line["amount"]
                if cod == "OVERTIME" :
                    overtime = line["amount"]
                if cod == "THR" :
                    thr = line["amount"]
                if cod == "BONUS" :
                    bonus = line["amount"]    
                if cod == "PKH" :
                    ketidakhadiran = line["amount"]
                if cod == "KSBN" :
                    kasbon = line["amount"]
                if cod == "CICILAN" :
                    cicilan = line["amount"]
                if cod == "GROSS" :
                    gross = line["amount"]
                if cod == "NET" :
                    net = line["amount"]
                if cod == "ZAKAT" :
                    zakat = line["amount"]
            self.write(cr,uid,[payslip.id],{
                "tunj_jabatan"      : int(tunj_jabatan),        
                "tunj_makan"        : int(tunj_makan),   
                "tunj_transport"    : int(tunj_transport),
                "lembur"            : int(overtime),
                "tidakhadir"        : int(ketidakhadiran),   
                "cashbon"           : int(kasbon), 
                "cicilan"           : int(cicilan),
                "total_tunjangan"   : int(gross), 
                "total_potongan"    : int(net-gross+zakat),   
                "net"               : int(net), 
                "thr"               : int(thr),
                "bonus"             : int(bonus),
                "zakat"             : int(zakat),      })
        return True

    def get_worked_day_lines(self, cr, uid, contract_ids, date_from, date_to, context=None):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        def was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            holiday_ids = self.pool.get('hr.holidays').search(cr, uid, [('state','=','validate'),('employee_id','=',employee_id),('type','=','remove'),('date_from','<=',day),('date_to','>=',day)])
            if holiday_ids:
                res = self.pool.get('hr.holidays').browse(cr, uid, holiday_ids, context=context)[0].holiday_status_id.name
            return res

        res = []
        jum_is = 0

        for contract in self.pool.get('hr.contract').browse(cr, uid, contract_ids, context=context):
            if not contract.working_hours:
                #fill only if the contract as a working schedule linked
                continue
            attendances = {
                 'name': _("Normal Working Days paid at 100%"),
                 'sequence': 1,
                 'code': 'WORK100',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,
            }
            presences = {
                 'name': _("Presences"),
                 'sequence': 2,
                 'code': 'PRESENCES',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            lembur = {
                 'name': _("Lembur"),
                 'sequence': 2,
                 'code': 'LEMBUR',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            tanpa_keterangan = {
                 'name': _("Tanpa keterangan"),
                 'sequence': 2,
                 'code': 'TK',
                 'number_of_days': 0.0,
                 'number_of_hours': 0.0,
                 'contract_id': contract.id,            
            }
            leaves = {}            
            day_from = datetime.strptime(date_from,"%Y-%m-%d")
            day_to = datetime.strptime(date_to,"%Y-%m-%d")
            nb_of_days = (day_to - day_from).days + 1

            tanpa_keterangan1 = 0.0
            
            for day in range(0, nb_of_days):
                working_hours_on_day = self.pool.get('resource.calendar').working_hours_on_day(cr, uid, contract.working_hours, day_from + timedelta(days=day), context)
                
                #menghitung lembur
                employee_id = contract.employee_id.id
                datas = day_from + timedelta(days=day)
    	        tanggal = datas.strftime("%Y-%m-%d")
    	    	obj_over = self.pool.get('hr.overtime')
    	        src_over = obj_over.search(cr,uid,[('employee_id','=',employee_id),('tanggal','=',tanggal),('state','=','validate')])
                for overt in obj_over.browse(cr,uid,src_over) :
    	            if overt.overtime_type_id.name == 'Lembur' :
    	                jumlah = overt.total_jam1
    	                jumlah_ril = overt.jam_lembur
    	                lembur['number_of_hours'] += jumlah

                if working_hours_on_day:
                    #the employee had to work
                    leave_type = was_on_leave(contract.employee_id.id, day_from + timedelta(days=day), context=context)
                    if leave_type:
                        #if he was on leave, fill the leaves dict
                        if leave_type in leaves:
                            leaves[leave_type]['number_of_days'] += 1.0
                            leaves[leave_type]['number_of_hours'] += working_hours_on_day
                        else:
                            leaves[leave_type] = {
                                'name': leave_type,
                                'sequence': 5,
                                'code': leave_type,
                                'number_of_days': 1.0,
                                'number_of_hours': working_hours_on_day,
                                'contract_id': contract.id,
                            }

                        # attendance
                        if leave_type == "IZIN" or leave_type == "SAKIT" :
                            jum_is += 1

                    else:
                    	
                    	#kehadiran
                    	real_working_hours_on_day = self.pool.get('hr.attendance').real_working_hours_on_day(cr,uid, contract.employee_id.id, day_from + timedelta(days=day),context)
                        if real_working_hours_on_day >= 0.000000000000000001 and leave_type == False :
	                        presences['number_of_days'] += 1.0
	                        presences['number_of_hours'] += working_hours_on_day

                        #add the input vals to tmp (increment if existing)
                        attendances['number_of_days'] += 1.0
                        attendances['number_of_hours'] += working_hours_on_day

            tanpa_keterangan['number_of_days'] = attendances['number_of_days'] - presences['number_of_days'] #- tanpa_keterangan1
            leaves = [value for key,value in leaves.items()]
            res += [attendances] + leaves + [presences] + [lembur] + [tanpa_keterangan]
        return res
    

        'jum_is' : fields.integer("Jumlah"),
        'jum_harikerja' : fields.char("Jumlah hari kerja"),
        'jum_harikerja1': fields.integer("jum hari kerja"),
        'izin' : fields.integer("Izin"),
        "tk" : fields.integer("TK"),
        ###### utuk Di Paysip ########
        "tunj_jabatan"          : fields.float("Tunjagan Jabatan"),
        "tunj_makan"            : fields.float("Tunjangan Makan"),
        "tunj_transport"        : fields.float("Tunjangan Transport"),
        "lembur"                : fields.float("Lembur"),
        "tidakhadir"             : fields.float("Terlambat"),
        "cashbon"               : fields.float("Kasbon"),
        "cicilan"               : fields.float("cicilan"),
        "total_tunjangan"       : fields.float("Total Tunjangan"),
        "total_potongan"        : fields.float("Total Potongan"),
        "net"                   : fields.float("Total"),
        "thr"                   : fields.float("THR"),
        "bonus"                 : fields.float("Bonus"),
        "zakat"                 : fields.float("zakat"),
        


hr_payslip()

class hr_attendance(osv.osv):
    _name = "hr.attendance"
    _inherit = "hr.attendance"

    def real_working_hours_on_day(self, cr, uid, employee_id, datetime_day, context=None):
        day = datetime_day.strftime("%Y-%m-%d 00:00:00")
        day2 = datetime_day.strftime("%Y-%m-%d 24:00:00")

        pprint.pprint(day)


        #employee attendance
        atts_ids = self.search(cr, uid, [('employee_id', '=', employee_id), ('name', '>', day), ('name', '<', day2)], limit=2, order='name asc' )
        
        time1=0
        time2=0

        for att in self.browse(cr, uid, atts_ids, context=context):
            if att.action == 'sign_in':
            	pprint.pprint('sign_in')
            	pprint.pprint(att.name)
                time1 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
            else:
            	pprint.pprint('sign_out')
            	pprint.pprint(att.name)
                time2 = datetime.strptime(att.name,"%Y-%m-%d %H:%M:%S")
        
        if time2 and time1:
	        delta = (time2 - time1).seconds / 3600.00
        else:
            delta = 0

        pprint.pprint(delta)        
        return delta

    def _altern_si_so(self, cr, uid, ids, context=None):
        """ Alternance sign_in/sign_out check.
            Previous (if exists) must be of opposite action.
            Next (if exists) must be of opposite action.

            PPI: skip _constraints supaya bisa import dari CSV
        """
        print "_altern_si_so"
        return True

hr_attendance()