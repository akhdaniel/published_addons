from openerp.osv import fields, osv
import datetime
import time
from datetime import date
from time import strptime
from time import strftime
from datetime import datetime
from openerp.tools.translate import _
from openerp import pooler
from openerp import tools
from openerp import SUPERUSER_ID

class hierarcy_history(osv.osv):
    _name = 'hr.hierarcy_history'

    _columns= {
        'employee_id' : fields.many2one('hr.employee'),
        'status_karyawan' : fields.selection([('aktif','Aktif'),('tidak_aktif','Tidak Aktif')],'Status Aktif'),
        'tgl' : fields.date('Tanggal Perubahan'),
        'status_kerja' : fields.char('Status Pegawai'),
        'golongan' :fields.many2one('hr_employs.gol','Golongan'),
        'jabatan' : fields.many2one('hr.job','Jabatan'),
        'dept_track' :fields.many2one('hr.department','Department'),
        'lokasi' : fields.char('Lokasi'),
    }
hierarcy_history()