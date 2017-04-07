from openerp import api, fields, models, _


class efaktur(models.Model):
    _name = 'vit.efaktur'

    
    terpakai = fields.Boolean(string="Terpakai", default=False, compute="_get_terpakai")
    name = fields.Char('Nomor eFaktur')


    def _get_terpakai(self):
        # apakah ada efaktur.id dipakai di account.invoice
        # pakai method search() di account.invoice
        for efaktur in self:
            ada = self.env['account.invoice'].search([('efaktur_id','=',efaktur.id)])
            if ada:
                efaktur.terpakai = True
            else:
                efaktur.terpakai = False
