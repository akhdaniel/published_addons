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

class employee(osv.osv):
    _name = "hr.employee"
    _inherit = 'hr.employee'

    def onchange_country1(self, cr, uid, ids, country_id1, context=None):
       result = {}
       country_id1_obj = self.pool.get('res.country')
       brew = country_id1_obj.browse(cr, uid, country_id1, context=context).code_telp
       return {'value':{'telp1': brew}}
       
    def onchange_country2(self, cr, uid, ids, country_id2, context=None):
       result = {}
       country_id1_obj = self.pool.get('res.country')
       brow = country_id1_obj.browse(cr, uid, country_id2, context=context).code_telp
       return {'value':{'telp2': brow}}
       
    def _compute_age(self, cr, uid, ids, usia, birthday, arg, context=None):
        # Fetch data structure and store it in object form
        records = self.browse(cr, uid, ids, context=context)
        result = {}
        # For all records in 'ids'
        for r in records:
            # In case 'birthdate' field is null
            usia = 0
            # If 'birthdate' field not null
            if r.birthday:
                # Encode string from 'birthdate' attribute
                d = strptime(r.birthday,"%Y-%m-%d")
                # Compute age as a time interval
                #delta = date(d[0], d[1], d[2]) - date.today()
                delta = date.today() - date(d[0], d[1], d[2])
                # Convert time interval to string value
                usia = delta.days / 365
            result[r.id] = usia
        return result    
           
    

        # 'hari_kerja' : fields.boolean('6 Hari kerja'),
        'nik': fields.char('NIK',20),
        'kelamin': fields.selection([('L','Pria'),('W','Wanita')],'Jenis Kelamin',required=False),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'agama':fields.many2one('hr_recruit.agama','Agama'),
        'birthday':fields.date('Tanggal Lahir'),
        'country_id': fields.many2one('res.country', 'Kewarganegaraan'),
        'ktp':fields.char('No ID',20),
        'no_pass':fields.char('No Passport',30),
        'no_rek':fields.char('No. Rekening',20),
        'no_sim':fields.char('No. SIM',30),
        'no_sima':fields.char('No. SIM A',30),
        'no_simc':fields.char('No. SIM C',30),
        'issued_id2':fields.many2one('res.country','Dikeluarkan di Negara'),
        'issued_id':fields.many2one('hr_recruit.kota','Dikeluarkan di'),
        'tgl_keluar_ktp':fields.date('Tanggal Dikeluarkan',),
        'tgl_berlaku':fields.date('Tanggal Berlaku'),
        'sim':fields.selection([('A','A'),('B1','B1'),('B2','B2'),('C','C')],'SIM'),
        'tgl_keluar_sim':fields.date('Tanggal Dikeluarkan SIM'),
        'tgl_keluar_sima':fields.date('Tanggal Dikeluarkan SIM A'),
        'tgl_keluar_simc':fields.date('Tanggal Dikeluarkan SIM C'),
        'type_id': fields.many2one('hr.recruitment.degree', 'Pendidikan'),
        'jurusan_id':fields.many2one('hr_recruit.jurusan_detail','Jurusan'),
        'result_id':fields.many2one('hr_recruit.result','Result'),
        'gelar_id':fields.many2one('hr_recruit.gelar','Gelar'),
        'alamat1':fields.char('Alamat',100),
        'prov_id':fields.many2one('hr_recruit.prov','Provinsi', domain="[('country_id','=',country_id1)]"),
        'kab_id':fields.many2one('hr_recruit.kota','Kab./kota', domain="[('provinsi_id','=',prov_id)]"),
        'kec_id':fields.many2one('hr_recruit.issued','Kecamatan', domain="[('kota_id','=',kab_id)]"),
        'alamat2':fields.char('Alamat',100),
        'prov_id2':fields.many2one('hr_recruit.prov','Provinsi', domain="[('country_id','=',country_id2)]"),
        'kec_id2':fields.many2one('hr_recruit.issued','Kecamatan', domain="[('kota_id','=',kab_id2)]"),
        'telp1':fields.char('Telepon',50),
        'telp2':fields.char('Telepon',50),
        'status':fields.selection([('single','Single'),('married','Menikah'),('duda','Duda'),('janda','Janda')],'Status Pernikahan'),
        'jml_anak':fields.integer('Jumlah Tanggungan'),
        'sjk_tanggal':fields.date('Sejak Tanggal'),        
        'employee_id' :fields.many2one('hr.employee'),
        'clas_id':fields.many2one('hr_employs.clas','Level'),
        'title_id':fields.many2one('hr.title','Title/Jabatan'),
        'extitle_id':fields.many2one('hr.extitle','Ex Title'),
        'gol_id':fields.many2one('hr_employs.gol','Golongan'),
        'wfield_id':fields.many2one('hr_employs.wfield','Bidang Pekerjaan'),
        'pansion_id':fields.many2one('hr_employs.pansion','Masa Pensiun'),
        'susunan_kel1_ids':fields.one2many('hr_employee.suskel1','employee_id','Susunan Keluarga'),
        'susunan_kel2_ids':fields.one2many('hr_employee.suskel2','employee_id','Susunan Keluarga'),
        'rwt_pend_ids':fields.one2many('hr_employee.rwt_pend','employee_id','Riwayat Pendidikan'),
        'bahasa_ids':fields.one2many('hr_employee.bahasa','employee_id','Bahasa'),
        'rwt_krj_ids':fields.one2many('hr_employee.rwt_krj','employee_id','Riwayat Pekerjaan'),
        'koneksi1_ids':fields.one2many('hr_employee.kon1','employee_id','Koneksi Internal'),
        'koneksi2_ids':fields.one2many('hr_employee.kon2','employee_id','Koneksi Eksternal'),
        'blood':fields.selection([('A','A'),('B','B'),('AB','AB'),('O','O')],'Gol Darah'),
        'bahasa2_id':fields.many2one('hr_recruit.bahasa2','Bahasa'),
        'kab_id2':fields.many2one('hr_recruit.kota','Kota', domain="[('provinsi_id','=',prov_id2)]"),
        'country_id2': fields.many2one('res.country', 'Negara'),
        'kodepos':fields.char('Kode Pos',8),
	    'kodepos1':fields.char('Kode Pos',8),
        'jenis_id':fields.selection([('Rek.Bank','Rekening Bank'),('KTP','Kartu Tanda Penduduk'),('Passport','Passport'),('SIM','SURAT IZIN MENGEMUDI'),('SIM_A','Surat Izin Mengemudi A'),('SIM_C','Surat Izin Mengemudi C')],'Jenis ID'),
        'pt_id':fields.many2one('hr_recruit.pt','Perguruan Tinggi'),
        ### field bidang id nanti di masukin di recruitment ####
        #'bidang_id':fields.related('jurusan_id','bidang_id',type='char',relation='hr_recruit.jurusan_detail',string='Bidang',readonly=True,store=True),  
	    'country_id1':fields.many2one('res.country','Negara'),
        'country_id2':fields.many2one('res.country','Negara'),
        'address_id2': fields.many2one('res.partner', 'Nama Kantor'),
        #'work_location2': fields.selection([('lucas','Lucas'),('marin','Marin')],'Lokasi Kerja',required=True), 
        'usia':fields.function(_compute_age, type='integer', obj='hr.employee', method=True, store=False, string='Usia (Thn)', readonly=True),        
        'ptkp_id': fields.many2one('hr.ptkp','Status Pajak', required=True),
        'npwp':fields.char('NPWP',size=20),
        'bid_id':fields.many2one('hr_recruit.bidang','Fakultas'), 
        'wage':fields.float('Proposed Salary'), 
        'npp' :fields.char('NPP', help="Nomor Pokok Perusahaan"),
        'npkj' :fields.char('NPKJ', help='Nomor Kepesertaan Jamsostek'), 
        'remaining_leaves' :fields.float('Remaining Legal Leavs',readonly=True),  
        'tgl_masuk' :fields.date('Tanggal Masuk'),
        'hierarcy_history' : fields.one2many('hr.hierarcy_history','employee_id','Hieracy History', readonly=True),
        'work_email' : fields.char('Email Kantor'),
        'work_phone' : fields.char('Telepon Kantor'),
        'coach_id' : fields.many2one('hr.employee', '',readonly=True),
        'ket_resign' : fields.char("Keterangan Resign"),
        'tgl_resign' : fields.date("Tanggal Resign"),
        'divisi_id' : fields.many2one('hr.divisi','Divisi', domain="[('department_id','=',department_id)]"),
        }

    _defaults = {    
        'nik': lambda self, cr, uid, context={}: self.pool.get('ir.sequence').get(cr, uid, 'hr.employee'),
        'jenis_id': 'KTP',
        'tgl_masuk' : lambda *a: time.strftime('%Y-%m-%d'),
                }
        
    def onchange_alamat(self, cr, uid, ids, address_id2, context=None):
        result = {}
        result2 = {}
        result3 = {}

        if address_id2:
            #import pdb;pdb.set_trace()
            address_id2_obj = self.pool.get('res.partner')
            result['street'] = address_id2_obj.browse(cr, uid, address_id2, context=context).street
            result2['phone'] = address_id2_obj.browse(cr, uid, address_id2, context=context).phone
            result3['email'] = address_id2_obj.browse(cr, uid, address_id2, context=context).email
            return {'value':{'work_location2': result['street'],'work_phone': result2['phone'],'work_email': result3['email']}}
        return {'value': {'work_location2': False,'work_phone': False,'work_email': False}}                 
employee()

#####################################################################################
#							     FILE MASTER										#
#####################################################################################


class divisi(osv.osv):
    _name = 'hr.divisi'


        'name' : fields.char("Divisi"),
        'department_id' : fields.many2one('hr.departmen','departmen'),
        'manager_id' : fields.many2one('hr.employee','Manager'),

divisi()

class susunan_keluarga1(osv.osv):
    _name='hr_employee.suskel1'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama',required=True),
        'kelamin':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'type_id': fields.many2one('hr.recruitment.degree', 'Pendidikan'),
        'pekerjaan':fields.char('Pekerjaan',60),
        'susunan':fields.selection([('Suami','Suami'),('Istri','Istri'),('anak1','Anak ke-1'),('anak2','Anak ke-2'),('anak3','Anak ke-3'),('anak4','Anak ke-4'),('anak5','Anak ke-5'),('anak6','Anak ke-6')],'Status Dalam Keluarga'),
        'no_id' : fields.char("No.ID")    
        
susunan_keluarga1()

class susunan_keluarga2(osv.osv):
    _name='hr_employee.suskel2'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'susunan':fields.selection([('Ayah','Ayah'),('Ibu','Ibu'),('anak1','Anak ke-1'),('anak2','Anak ke-2'),('anak3','Anak ke-3'),('anak4','Anak ke-4'),('anak5','Anak ke-5'),('anak6','Anak ke-6')],'Status Dalam Keluarga'),
        'name':fields.char('Nama'),
        'kelamin':fields.selection([('L','Laki-Laki'),('P','Perempuan')],'Jenis Kelamin'),
        'kota_id':fields.many2one('hr_recruit.kota','Tempat Lahir'),
        'tgl_lahir':fields.date('Tanggal Lahir'),
        'type_id':fields.many2one('hr.recruitment.degree', 'Pendidikan',50),
        'pekerjaan':fields.char('Pekerjaan',60),
            }
susunan_keluarga2()   

class rwt_pendidikan(osv.osv):
    _name='hr_employee.rwt_pend'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama Sekolah',128,required=True),
        'jurusan':fields.many2one('hr_recruit.jurusan_detail','Jurusan'),
        'tempat':fields.text('Alamat'),
        'tahun_msk':fields.date('Tahun Masuk'),
        'tahun_klr':fields.date('Tahun Keluar'),
        'ijazah':fields.many2one('hr.recruitment.degree','Ijazah yang Diperoleh'),
            }
rwt_pendidikan()      

class bahasa(osv.osv):
    _name='hr_employee.bahasa'
    
    _columns= {
        'employee_id':fields.many2one('hr.employee','Applicant'),        
        'name':fields.many2one('res.country', 'Bahasa',required=True),
        'tulis':fields.many2one('hr_recruit.b_tulisan','Tertulis'),
        'lisan':fields.many2one('hr_recruit.b_lisan','Lisan'),
            }
bahasa()    

class rwt_pekerjaan(osv.osv):
    _name='hr_employee.rwt_krj'
    
    _columns= {
        'no':fields.integer('Nomor'),
        'employee_id':fields.many2one('hr.employee'), 
        'name':fields.char('Nama Perusahaan',60,required=True),
        'tempat':fields.text('Alamat'),
        'tahun_msk':fields.date('Tahun Masuk'),
        'tahun_klr':fields.date('Tahun Keluar'),
        'jabatan':fields.char('Jabatan',30),
        'gaji':fields.float('Gaji'),
        'alasan':fields.char('Alasan Pindah',30),
            }
rwt_pekerjaan()

class koneksi1(osv.osv):
    _name='hr_employee.kon1'
    
    _columns={        
        'employee_idd':fields.char('Nama',),
        'employee_id':fields.many2one('hr.employee','Nama',required=True),
        'job_id':fields.related('employee_id','job_id',type='many2one',relation='hr.job',string='Jabatan',readonly=True),
        'alamat':fields.related('employee_id','department_id',type='many2one',relation='hr.department',string='departmen',readonly=True), 
        'telepon':fields.char('Telepon',25),
            }
koneksi1()

class koneksi2(osv.osv):
    _name='hr_employee.kon2'
    
    _columns={        
        'employee_id':fields.many2one('hr.employee'),
        'name':fields.char('Nama',60),
        'alamat':fields.text('Alamat/Telepon'),
        'jabatan':fields.char('Jabatan',30),
        'telepon':fields.char('Telepon',25),
            }
koneksi2()

class bahasa2(osv.osv):
    _name='hr_recruit.bahasa2'
    
    _columns= {       
        'name':fields.char('Nama Bahasa',30,required=True),
            }
bahasa2()

class clas(osv.osv):
    _name='hr_employs.clas'
    
    _columns= {       
        'name':fields.char('Class',50,required=True),
            }
clas()

class title(osv.osv):
    _name='hr_employs.title'
    
    _columns= {       
        'name':fields.char('Title',50,required=True),
            }
title()

class extitle(osv.osv):
    _name='hr_employs.extitle'
    
    _columns= {       
        'name':fields.char('Ex Title',50,required=True),
            }
extitle()

class golongan(osv.osv):
    _name='hr_employs.gol'
    
    _columns= {       
        'name':fields.char('Golongan',20,required=True),
        'rec':fields.char('record'),
        'no' : fields.char('Urutan')
            }
golongan()

class wfield(osv.osv):
    _name='hr_employs.wfield'
    
    _columns= {       
        'name':fields.char('Bidang Pekerjaan',50,required=True),
            }
wfield()

class pansion(osv.osv):
    _name='hr_employs.pansion'
    
    _columns= {       
        'name':fields.char('Masa Pensiun',50,required=True),
            }
pansion()

class country(osv.osv):
    _name = "res.country"
    _inherit = "res.country"
    

        "code_telp" : fields.char("Kode Telp"),

country()