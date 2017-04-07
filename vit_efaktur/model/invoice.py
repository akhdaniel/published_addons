from openerp import api, fields, models


class invoice(models.Model):
	_name = 'account.invoice'
	_inherit = 'account.invoice'


	efaktur_id = fields.Many2one(comodel_name="vit.efaktur", string="Nomor eFaktur")
	# 							compute="_efaktur_id",required= False)

	# def _efaktur_id(self):
	# 	for rec in self:
	# 		for invoice in self.env['account.invoice'].search([('number','=',rec.name)]):
	# 			for efaktur in self.env['vit.efaktur'].search([('terpakai','=',rec.name)]):
	# 				if invoice.state=='terpakai':
	# 					rec.efaktur_id=''







	# def _cek_terpakai(self, cr, uid, ids, context=None):

	# 	efaktur = self.browse(cr, uid, ids, context=context)

	# 	for efaktur in self:
	# 		# x = array of partner_id.id yang ada di session.attendee_ids 
	# 		# misal x = [1,2,4,5,6,9]
	# 		# for att in session.attendee_ids:
	# 		# 		x.append(att.partner_id.id)
	# 		x = [att.efaktur_id.id for att in invoice.efaktur_id]
	# 		if efaktur.terpakai.id in x:
	# 			return False 

	# 		return True

	
 	# constraints : [ (nama_function , message, fields) ]
	# _sql_constraints = [('Nomor_eFaktur_unique' , 'UNIQUE(efktur_id,name)',
	# 					'You Cannot Insert the same efaktur number!!!'),]


	_sql_constraints = [('uniq_efaktur', 'unique(efaktur_id)', "Nomor eFaktur tidak boleh digunakan oleh invoice lain !")]
	
