from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class partner(models.Model):
    _name = 'res.partner'
    _inherit = 'res.partner'
    
    npwp = fields.Char(string="NPWP", required=False, )
    LT = fields.Char("LT", default="LT")
    NAMA = fields.Char("NAMA", compute="_get_name")
    JALAN = fields.Char("JALAN", compute="_get_street")
    BLOK = fields.Char("BLOK")
    NOMOR = fields.Char("NOMOR")
    RT = fields.Char("RT")
    RW = fields.Char("RW")
    KECAMATAN = fields.Char("KECAMATAN")
    KELURAHAN = fields.Char("KELURAHAN")
    KABUPATEN = fields.Char("KABUPATEN", compute="_get_city")
    PROPINSI = fields.Char("PROPINSI", compute="_get_state")
    KODE_POS = fields.Char("KODE_POS", compute="_get_zip")
    NOMOR_TELEPON = fields.Char("NOMOR_TELEPON", compute="_get_phone")
    
    def _get_name(self):
        for cust in self:
            cust.NAMA = cust.name
            
    def _get_street(self):
        for cust in self:
            cust.JALAN = cust.street if cust.street else '' + ' ' + cust.street2 if cust.street2 else ''

    def _get_city(self):
        for cust in self:
            cust.KABUPATEN = cust.city
    
    def _get_state(self):
        for cust in self:
            cust.PROPINSI = cust.state_id.name
    
    
    def _get_zip(self):
        for cust in self:
            cust.KODE_POS = cust.zip
    
    def _get_phone(self):
        for cust in self:
            cust.NOMOR_TELEPON = cust.phone
    
