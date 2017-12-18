from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)


class outbox_wizard(models.TransientModel):
    _name = 'vit_sms.outbox.wizard'
    group_ids       = fields.Many2many(comodel_name="vit_sms.group", string="Groups", )
    partner_ids     = fields.Many2many(comodel_name="res.partner", string="Partners", )
    additional_destination = fields.Char("Additional Destination", help="Comma separated mobile numbers")
    destination     = fields.Char(string="Destination",
                                  compute="_compute_destination",
                                  readonly=True,
                                  store=True,
                                  help="Comma separated. Automatically filled with destination mobile numbers of group members or mobile phone number of Partners")
    message         = fields.Text(string="Message", required=True, )
    send_datetime   = fields.Datetime(string="Send datetime", required=False, default=lambda self: time.strftime("%Y-%m-%d %H:%M:%S"))
    is_immediate    = fields.Boolean(string="Imediate sending?", default=False )


    @api.multi
    def confirm_button(self):
        # create outbox for each destinations
        outbox = self.env['vit_sms.outbox']
        for dest in self.destination.split(","):
            data = {
                'destination'   : dest,
                'message'       : self.message,
                'send_datetime' : self.send_datetime,
                'is_immediate'  : self.is_immediate,
                'state'         : 'open',
            }
            outbox.create(data)
        return

    @api.depends("group_ids","partner_ids","additional_destination")
    def _compute_destination(self):
        dest = [ p.mobile for p in self.partner_ids if p.mobile]
        for g in self.group_ids:
            dest += [p.mobile for p in g.partner_ids if p.mobile]
        add = self.additional_destination.split(",") if self.additional_destination else []
        dest += add
        self.destination = ",".join(dest)

