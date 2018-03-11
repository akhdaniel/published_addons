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

    outbox_ids      = fields.One2many(comodel_name="vit_sms.outbox", inverse_name="send_sms_id", string="Outbox", required=False, )
    sent_ids        = fields.One2many(comodel_name="vit_sms.sent", inverse_name="send_sms_id", string="Sent", required=False, )

    prefixes        = fields.Char(string="Prefix", required=False, help="Allowed prefix, comma separated values, eg: 062,+62,08")

    @api.multi
    def action_cancel(self):
        self.env.cr.execute("delete from vit_sms_outbox where send_sms_id=%s", (self.id,) )
        self.env.cr.execute("delete from vit_sms_sent where send_sms_id=%s", (self.id,) )
        self.state = 'draft'

    @api.multi
    def action_confirm(self):
        # create outbox for each destinations
        outbox = self.env['vit_sms.outbox']
        for dest in self._compute_destination():
            data = {
                'destination'   : self.normalize_number(dest.phone),
                'message'       : self.replace_tokens(dest),
                'send_datetime' : self.send_datetime,
                'is_immediate'  : self.is_immediate,
                'state'         : 'open',
                'send_sms_id'   : self.id
            }
            outbox.create(data)

        if self.additional_destination:
            for dest in self.additional_destination.split(","):
                data = {
                    'destination'   : self.normalize_number(dest),
                    'message'       : self.message,
                    'send_datetime' : self.send_datetime,
                    'is_immediate'  : self.is_immediate,
                    'state'         : 'open',
                    'send_sms_id'   : self.id
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

    def normalize_number(self, phone):
        res = phone.replace(" ","")
        res = res.replace("-","")
        return res

    def _compute_destination(self):

        prefixes = self.prefixes.split(",")

        # partner_ids
        dest = [ p for p in self.partner_ids if p.phone]

        # group_ids
        for g in self.group_ids:
            dest += [p for p in g.partner_ids if p.phone]

        # partner domain
        if self.partner_domain:
            partners = self.env['res.partner'].search(eval(self.partner_domain))
            dest += [ p for p in partners if p.phone]

        # remove non prefix
        dups = [d for d in dest if (d.phone[:2] in prefixes or d.phone[:3] in prefixes or d.phone[:4] in prefixes)]

        # remove duplicates
        nodups=[]
        nodup_phones = list(set([p.phone for p in dups]))

        for ph in nodup_phones:
            for p in dups:
                if ph == p.phone:
                    nodups.append(p)
                    break

        return nodups

