from openerp import api, fields, models, _


class efaktur(models.Model):
    _name = 'vit.efaktur'

    
    terpakai = fields.Boolean(string="Terpakai", default=False)
    name = fields.Char('Nomor eFaktur')
