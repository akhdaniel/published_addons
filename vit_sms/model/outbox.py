from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)
STATES=[('draft', 'Draft'), ('open', 'Sending'), ]
MAX_RETRY = 3

class outbox(models.Model):
    _name = 'vit_sms.outbox'
    _inherit = ['mail.thread', 'ir.needaction_mixin']

    name            = fields.Char("Rec. Number", readonly=True)
    destination     = fields.Char("Destination",
                              help="Destination mobile numbers of group members or mobile phone number of Partners")
    message         = fields.Char(string="Message", required=True, size=160)
    send_datetime   = fields.Datetime(string="Send datetime", required=False, default=lambda self: time.strftime("%Y-%m-%d %H:%M:%S"))
    is_immediate    = fields.Boolean(string="Imediate sending?", default=False )

    config_id       = fields.Many2one(comodel_name="vit_sms.config", string="Gateway Config", required=False, )

    state           = fields.Selection(string="State", selection=STATES, required=False, default='draft')
    error_message   = fields.Char("Error Message")
    retry           = fields.Integer(string="Retry", required=False, default=0)

    messageid       = fields.Char(string="Message ID", required=False, help="Tracking for delivery report")
    send_sms_id     = fields.Many2one(comodel_name="vit_sms.send_sms", string="Send SMS", required=False, )

    @api.model
    def create(self, vals):
        vals['name']    = self.env['ir.sequence'].next_by_code('vit_sms.outbox.seq')
        return super(outbox, self).create(vals)

    @api.multi
    def action_send(self):
        (status, error_message, messageid) = self.send_gateway()

        if status == 0 :
            state = 'sent'
        else:
            state = 'failed'

        self.error_message = error_message
        self.messageid = messageid
        self.move_to_sent(state)

    @api.multi
    def action_schedule(self):
        self.state=STATES[1][0]

    @api.multi
    def action_cancel(self):
        self.state=STATES[0][0]

    def move_to_sent(self, state):
        sent=self.env['vit_sms.sent']
        sent.create({
            'name'          : self.name,
            'destination'   : self.destination,
            'message'       : self.message,
            'send_datetime' : self.send_datetime,
            'is_immediate'  : self.is_immediate,
            'state'         : state,
            'error_message' : self.error_message,
            'retry'         : self.retry,
            'messageid'     : self.messageid,
            'send_sms_id'   : self.send_sms_id.id ,
        })
        self.unlink()

    def process_outbox(self):
        for out in self.search([('state','=','open'),
                                ('send_datetime','<',time.strftime('%Y-%m-%d %H:%M:%S'))]):

            (status,error_message, messageid) = out.send_gateway()

            out.messageid=messageid
            out.error_message=error_message

            if status == 0 or out.retry > MAX_RETRY:
                if out.retry < MAX_RETRY:
                    state = 'sent'
                else:
                    state='failed'
                out.move_to_sent(state)
            else:
                out.retry = out.retry + 1

            self.env.cr.commit()


    def send_gateway(self):
        _logger.info('send_gateway to be implemented in gateway specific addon')
        return (0,'','')
    
    
    def send_sms(self, destination, message, send_datetime=False, is_immediate=False):

        if not send_datetime:
            send_datetime = time.strftime("%Y-%m-%d %H:%M:%S")

        data = {
            'name'          : False,
            'group_ids'     : False,
            'partner_ids'   : False,
            'destination'   : destination,
            'message'       : message,
            'send_datetime' : send_datetime,
            'is_immediate'  : is_immediate,
            'state'         : STATES[1][0],

        }
        out = self.create(data)

        if is_immediate:
            (status, error_message, messageid) = out.send_gateway()
            if status == 0:
                state = 'sent'
            else:
                state = 'failed'

            out.error_message = error_message
            out.messageid=messageid
            out.move_to_sent(state)

    @api.multi
    def action_test_send(self):
        destination = "6281320379277"
        message = "test send message via api"
        self.send_sms(destination, message, send_datetime=False, is_immediate=False)
        self.send_sms(destination, message+ " immediate", send_datetime=False, is_immediate=True)
