from odoo import tools
from odoo import api,fields,models
import openerp.addons.decimal_precision as dp
import time
import logging
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class anggaran_category(models.Model):
    _name         = "anggaran.category"
    code = fields.Char('Kode')
    name = fields.Char('Nama')


class kebijakan(models.Model):
    """
    level 1 MAK
    """
    _name         = "anggaran.kebijakan"

    name = fields.Text(_('Nama'), required=True)
    code = fields.Char(_('Kode'), required=True)
    tridharma_id = fields.Many2one('anggaran.tridharma', _('Tri Dharma PT'))
    category_id = fields.Many2one('anggaran.category', _('Kategori'))
    program_ids  = fields.One2many('anggaran.program','kebijakan_id','Programs', ondelete="cascade")

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            if record.name and record.code:
                result.append((record.id, record.code + ' ' + record.name))
            if record.name and not record.code:
                result.append((record.id, record.name))
        return result


    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.browse()
        if name:
            recs = self.search(['|',('name', '=', name),('code', '=', name)] + args, limit=limit)
        if not recs:
            recs = self.search([('name', operator, name)] + args, limit=limit)
        return recs.name_get()


