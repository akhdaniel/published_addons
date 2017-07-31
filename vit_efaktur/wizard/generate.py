from openerp import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)


class efaktur_wizard(models.TransientModel):
    _name = 'vit.generate_efaktur'
    
    start   = fields.Char("Start")
    end     = fields.Char("End")
    
    @api.multi
    def confirm_button(self):
        start = self.start
        end = self.end
        
        #040.001-17.00000010
        #a=["040", "001-17", "00000010"]
        #b=["040", "001-17", "00000110"]
        a = start.split(".")
        b = end.split(".")
        
        for i in range(int(a[2]), int(b[2])+1):
            nomor = "%s.%s.%08d" % (a[0],a[1],i)
            data = {
                'name': nomor,
            }
            self.env['vit.efaktur'].create(data)
        
        return
    
