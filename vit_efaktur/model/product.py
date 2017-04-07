from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class product(models.Model):
    _name = 'product.product'
    _inherit = 'product.product'

    OB 		        = fields.Char("OB", default="OB")
    KODE_OBJEK 		= fields.Char("KODE_OBJEK", compute="_get_code")
    NAMA 		    = fields.Char("NAMA", compute="_get_name")
    HARGA_SATUAN 	= fields.Char("HARGA_SATUAN", compute="_get_sale_price")
    
    def _get_code(self):
        for product in self:
            product.KODE_OBJECT = product.default_code
            
    def _get_name(self):
        for product in self:
            product.NAMA = product.display_name
            
    def _get_sale_price(self):
        for product in self:
            product.HARGA_SATUAN = product.list_price
            
            
            