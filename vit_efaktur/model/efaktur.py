from openerp import api, fields, models, _


class efaktur(models.Model):
    _name = 'vit.efaktur'

    
    terpakai = fields.Boolean(string="Terpakai",
                              compute="_get_terpakai",
                              store=True,
                              default=False,
                              )
    name = fields.Char('Nomor eFaktur')
    
    invoice_ids = fields.One2many(comodel_name="account.invoice",
                                  inverse_name="efaktur_id",
                                  string="Invoices",
                                  required=False, )
    

    @api.depends('invoice_ids')
    def _get_terpakai(self):
        # apakah ada efaktur.id dipakai di account.invoice
        # pakai method search() di account.invoice
        for efaktur in self:
            ada = self.env['account.invoice'].search([('efaktur_id','=',efaktur.name)])
            if ada:
                efaktur.terpakai = True
            else:
                efaktur.terpakai = False
