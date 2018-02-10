from openerp.osv import fields, osv
from openerp.tools.translate import _

class pkp(osv.osv):
    _name= "hr.pkp"
    _rec_name= "kode"
    

        "kode": fields.char('Kode',size= 5, required=True),
        "nominal_min" :fields.float("Nominal Min", required=True),
        "nominal_max" :fields.float("Nominal Max", required=True),
        "pajak": fields.float('Pajak (%)',size= 2, required=True),

    '''
    def _check_nominal(self, cr, uid, ids):
        for nominal in self.browse(cr, uid, ids):
            nominal_id = self.search(cr, uid, [('nominal_min', '>', nominal.nominal_max), ('nominal_max', '<', nominal.nominal_min)])
            if nominal_id:
                return False
        return True

    _constraints = [
        (_check_nominal, 'range max tidak boleh lebih kecil dari range min!', ['nominal_min','nominal_max']),
                    ]
    '''
    _sql_constraints = [('kode_uniq', 'unique(kode)', 'Kode tidak boleh sama!')]
    
    _sql_constraints = [('pajak_uniq', 'unique(pajak)', 'Besaran % pajak tidak boleh sama!')]

pkp()

class ptkp(osv.osv):
    _name= "hr.ptkp"
    _rec_name= "kode"
    

        "kode":fields .char('Kode',size=5 , required=True),
        "nominal_bulan" :fields.float("Nominal Perbulan", required=True),
        "nominal_tahun" :fields.float("Nominal Pertahun"),

    def onchange_kali(self, cr, uid, ids, nominal_bulan, nominal_tahun, context=None):
        v = {'nominal_tahun_': (nominal_bulan )* 12}
        return {'value': v}
    
    def onchange_bagi(self, cr, uid, ids, nominal_bulan, nominal_tahun, context=None):
        v = {'nominal_bulan': (nominal_tahun )/12 }
        return {'value': v}
    
    _sql_constraints = [('kode_uniq', 'unique(kode)', 'Kode tidak boleh sama!')]

ptkp()
