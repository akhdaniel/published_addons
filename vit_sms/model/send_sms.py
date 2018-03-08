from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class send_sms(models.Model):

    _name = 'vit_sms.send_sms'
    group_ids       = fields.Many2many(comodel_name="vit_sms.group", string="Groups", )
    partner_ids     = fields.Many2many(comodel_name="res.partner", string="Partners", )
    partner_domain = fields.Char(string="Partner Search Domain", required=False, default="[('phone','!=',False)]" )
    additional_destination = fields.Char("Additional Destination", help="Comma separated phone numbers")
    message         = fields.Text(string="Message", required=True,
                                  help="Message to send, max 160 chars. Available tokens: {name}, {street}, {city}, {country}", size=160)
    send_datetime   = fields.Datetime(string="Send datetime", required=False, default=lambda self: time.strftime("%Y-%m-%d %H:%M:%S"))
    is_immediate    = fields.Boolean(string="Imediate sending?", default=False )
    state           = fields.Selection(string="State", default='draft',
                                       selection=[('draft', 'Draft'), ('done','Done') ], required=False, )


    @api.multi
    def action_cancel(self):
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        # create outbox for each destinations
        outbox = self.env['vit_sms.outbox']
        for dest in self._compute_destination():
            data = {
                'destination'   : dest.phone,
                'message'       : self.replace_tokens(dest),
                'send_datetime' : self.send_datetime,
                'is_immediate'  : self.is_immediate,
                'state'         : 'open',
            }
            outbox.create(data)

        if self.additional_destination:
            for dest in self.additional_destination.split(","):
                data = {
                    'destination'   : dest,
                    'message'       : self.message,
                    'send_datetime' : self.send_datetime,
                    'is_immediate'  : self.is_immediate,
                    'state'         : 'open',
                }
                outbox.create(data)

        self.state = 'done'

        return

    def replace_tokens(self, dest):
        res = self.message.replace('{name}', dest.name)
        res = res.replace('{street}', dest.street if dest.street else '')
        res = res.replace('{city}', dest.city if dest.city else '')
        res = res.replace('{country}', dest.country_id.name if dest.country_id else '')
        return res


    @api.depends("group_ids","partner_ids","additional_destination")
    def _compute_destination(self):
        # partner_ids
        dest = [ p for p in self.partner_ids if p.phone]

        # group_ids
        for g in self.group_ids:
            dest += [p for p in g.partner_ids if p.phone]

        # partner domain
        if self.partner_domain:
            partners = self.env['res.partner'].search(eval(self.partner_domain))
            dest += [ p for p in partners if p.phone]

        return dest

