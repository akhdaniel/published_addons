from openerp.osv import fields, osv

class title(osv.osv):
    _name='hr.title' 
    
    _columns ={
        'name' : fields.char('Description'),
        'digit':fields.integer('Digit'),
        'code':fields.char('Code'),
        'urutan':fields.char("Urutan"),
    }
title

class extitle(osv.osv):
    _name='hr.extitle' 
    

        'name' : fields.char('Description'),
        'digit':fields.integer('Digit'),
        'code':fields.char('Code')
    
extitle()

class kota(osv.osv):
    _name='hr_recruit.kota'
    
    _columns={
        'name':fields.char('Nama Kab./Kota',50),
        'provinsi_id' : fields.many2one('hr_recruit.prov','Provinsi'),
        }
kota()

class agama(osv.osv):
    _name='hr_recruit.agama'
        
    _columns={
        'name':fields.char('Agama',30),
        }
agama()                    

class issued(osv.osv):
    _name='hr_recruit.issued'
        
    _columns={
        'name':fields.char('Kecamatan',50),
        'kota_id':fields.many2one('hr_recruit.kota','Kota'),
        }
issued()

class result(osv.osv):
    _name='hr_recruit.result'
        
    _columns={
        'name':fields.char('Result',50),
        }
result()  

class gelar(osv.osv):
    _name='hr_recruit.gelar'
        
    _columns={
        'name':fields.char('Gelar',50),
        }
gelar()

class pt(osv.osv):
    _name='hr_recruit.pt'
        
    _columns={
        'name':fields.char('Nama Perguruan Tinggi',50),
        }
pt()

class bidang(osv.osv):
    _name='hr_recruit.bidang'
        
    _columns={
        'name':fields.char('Bidang',50),
        }
bidang()

class provinsi(osv.osv):
    _name='hr_recruit.prov'
        
    _columns={
        'name':fields.char('Provinsi',50),
        'country_id':fields.many2one('res.country','Negara'),
        }
provinsi()

class b_lisan(osv.osv):
    _name='hr_recruit.b_lisan'
        
    _columns={
        'name':fields.char('Lisan',20),
        }
b_lisan()

class b_tulisan(osv.osv):
    _name='hr_recruit.b_tulisan'
        
    _columns={
        'name':fields.char('Tulisan',20),
        }
b_tulisan()

class pendidikan(osv.osv):
    _name='hr_recruit.pendidikan'
    
    _columns= {
        'name':fields.char('Pendidikan',25,required=True),
        #'jurusan':fields.one2many('hr_recruit.jurusan','pendidikan_id','Jurusan'),
            }
pendidikan()

class jurusan(osv.osv):
    _name='hr_recruit.jurusan'
    
    _columns= {
        'name':fields.many2one('hr_recruit.jurusan_detail','Jurusan',required=True),
        #'pendidikan_id':fields.many2one('hr_recruit.pendidikan'),
        'permohonan_recruit_id':fields.many2one('hr.job','Pekerjaan'),
            }
jurusan()

class jurusan_detail(osv.osv):
    _name='hr_recruit.jurusan_detail'
    
    _columns= {
        'bidang_id':fields.many2one('hr_recruit.bidang','Bidang'),
        'name':fields.char("Jurusan",required=True),       
            }
jurusan_detail()

class fasilitas(osv.osv):
    _name = "hr.fasilitas"
    _rec_name="fasilitas"
    

        "fasilitas" : fields.many2one("hr.fasilitas3","Fasilitas",required=True),
        "applican_id" : fields.many2one("hr.applicant","Fasilitas"),
    
fasilitas()

class fasilitas2(osv.osv):
    _name = "hr.fasilitas2"
    _rec_name="fasilitas"
    

        "fasilitas" : fields.many2one("hr.fasilitas3","Fasilitas",required=True),
        "applican_id" : fields.many2one("hr.applicant","Fasilitas"),
    
fasilitas()

class fasilitas3(osv.osv):
    _name = "hr.fasilitas3"
    

        "name" : fields.char("Fasilitas",required=True),
    
fasilitas3()