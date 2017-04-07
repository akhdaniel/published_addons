from openerp import api, fields, models


class invoice(models.Model):
	_name = 'account.invoice'
	_inherit = 'account.invoice'


	efaktur_id = fields.Many2one(
		comodel_name="vit.efaktur",
		string="Nomor eFaktur"
	)
