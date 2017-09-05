from odoo import api, fields, models, _
import logging
_logger = logging.getLogger(__name__)

class sale(models.Model):
    _name = 'sale.order'
    _inherit = 'sale.order'

    @api.depends('amount_untaxed','po_id')
    def _hitung_margin(self):
        for rec in self:
            rec.margin = rec.amount_untaxed - rec.po_id.amount_untaxed

    @api.model
    def create(self):
        # jika state masih draft/sent: ambil sequence Q
        pass

    @api.model
    def action_confirm(self):
        # update name =  sequence SO
        pass

    po_id = fields.Many2one(comodel_name="purchase.order", string="Purchase order", required=False, )

    margin = fields.Float(string="Margin SO/PO",  required=False, compute='_hitung_margin')



