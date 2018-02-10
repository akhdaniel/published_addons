from odoo import api, fields, models, _
import time
from odoo.exceptions import UserError
import logging
_logger = logging.getLogger(__name__)

class NewModule(models.Model):
    _name = 'mail.mass_mailing'
    _inherit = 'mail.mass_mailing'


    def send_mail(self):
        batch_size = int(self.env['ir.config_parameter'].sudo().get_param('mail.batch_size')) or self._batch_size
        _logger.info("======= sending emails with batch_size=%s" % batch_size)

        author_id = self.env.user.partner_id.id
        for mailing in self:
            # instantiate an email composer + send emails
            res_ids = mailing.get_remaining_recipients()
            if not res_ids:
                raise UserError(_('Please select recipients.'))

            sliced_res_ids = [res_ids[i:i + batch_size] for i in range(0, len(res_ids), batch_size)]
            if not sliced_res_ids:
                raise UserError(_('No more recipients.'))


            # Convert links in absolute URLs before the application of the shortener
            mailing.body_html = self.env['mail.template']._replace_local_links(mailing.body_html)

            composer_values = {
                'author_id': author_id,
                'attachment_ids': [(4, attachment.id) for attachment in mailing.attachment_ids],
                'body': mailing.convert_links()[mailing.id],
                'subject': mailing.name,
                'model': mailing.mailing_model,
                'email_from': mailing.email_from,
                'record_name': False,
                'composition_mode': 'mass_mail',
                'mass_mailing_id': mailing.id,
                'mailing_list_ids': [(4, l.id) for l in mailing.contact_list_ids],
                'no_auto_thread': mailing.reply_to_mode != 'thread',
            }
            if mailing.reply_to_mode == 'email':
                composer_values['reply_to'] = mailing.reply_to

            composer = self.env['mail.compose.message'].with_context(active_ids=sliced_res_ids[0]).create(composer_values)
            composer.with_context(active_ids=sliced_res_ids[0]).send_mail(auto_commit=True)

            if len(sliced_res_ids)==1:
                mailing.state = 'done'

        return True
