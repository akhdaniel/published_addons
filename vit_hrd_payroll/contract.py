from openerp.osv import fields, osv
import time
from datetime import date
from datetime import datetime
from datetime import timedelta
from dateutil import relativedelta
from dateutil.relativedelta import relativedelta
from openerp.tools.translate import _



class hr_contract(osv.osv):
    _name = 'hr.contract'
    _inherit = 'hr.contract'


    	'jenis_tunjangan'		: fields.many2one('hr.contract_tunjangan', 'Golongan'),
    	'contract_type_id'		: fields.many2one('hr.contract_tunjangan', 'Golongan'),
        "tunj_jabatan"          : fields.float("Tunjangan Jabatan"),
        "tunj_makan"            : fields.float("Tunjangan Makan"),
        "tunj_transport"        : fields.float("Tunjangan Transport"),
        "tunj_komunikasi"       : fields.float("Tunjangan Komunikasi"),
        "zakat" : fields.boolean("Zakat Penghasilan")

    
hr_contract()

class hr_contract_type(osv.osv):
    _name = 'hr.contract.type'
    _inherit = 'hr.contract.type'


    	"jams1":fields.float('Tunjangan BPJS Ketenagakerjaan (%)'),
        "jams2":fields.float('Potongan BPJS Ketenagakerjaan (%)'),
        "jams3":fields.float('Tunjangan BPJS Kesehatan (%)'),
        "jams4":fields.float('Potongan BPJS Kesehatan (%)'),

        "pajak": fields.float('Pajak (%)'),
        "reimburse_pengobatan": fields.float('Pengobatan Tahunan', size=1,
                                             help='Digit dikalikan dengan gaji pokok karyawan'),
        "reimburse_perawatan": fields.float('Perawatan Rumah Sakit', size=1,
                                            help='Digit dikalikan dengan gaji pokok karyawan'),
        "biaya_jabatan": fields.float('Biaya Jabatan (%)', size=1),
        "max_biaya_jabatan": fields.float('Nominal Max (Rp)'),
        "tht": fields.float('Kontribusi Perusahaan (%)'),
        'ttht': fields.float('Kontribusi Karyawan (%)'),
        'max_tht': fields.float('Nominal Max (Rp)'),
        'range_pengobatan': fields.float('Batas Pengobatan', help='batas maksimal pengobatan'),
        'type_perhitungan_pajak': fields.selection([('net', 'NET'), ('gross_up', 'Gross Up'), ('mix', 'MIX')],
                                                   'Type perhitungan Pajak', required=True)
    

hr_contract_type()

class hr_contract_tunjangan(osv.osv):
    _name = 'hr.contract_tunjangan'


    	"name"              : fields.char("Golongan"),
        "tunj_jabatan"      : fields.float("Tunjangan Jabatan"),
        "tunj_makan"        : fields.float("Tunjangan Makan"),
        "tunj_transport"    : fields.float("Tunjangan Transport"),
        "tunj_komunikasi"   : fields.float("Tunjangan Komunikasi"),


hr_contract_tunjangan()