from odoo import api, fields, models, _
import threading
import datetime

import logging
_logger = logging.getLogger(__name__)

class NewModule(models.Model):
    _name = 'mail.mail'
    _inherit = 'mail.mail'


    @api.model
    def process_email_queue(self, ids=None):
        """Send immediately queued messages, committing after each
           message is sent - this is not transactional and should
           not be called during another transaction!

           :param list ids: optional list of emails ids to send. If passed
                            no search is performed, and these ids are used
                            instead.
           :param dict context: if a 'filters' key is present in context,
                                this value will be used as an additional
                                filter to further restrict the outgoing
                                messages to send (by default all 'outgoing'
                                messages are sent).
        """
        if not self.ids:
            limit = self.env['ir.config_parameter'].sudo().get_param('mail.send_limit','100')
            _logger.info("======= sending emails with limit=%s" % limit)
            filters = ['&',
                       ('state', '=', 'outgoing'),
                       '|',
                       ('scheduled_date', '<', datetime.datetime.now()),
                       ('scheduled_date', '=', False)]
            if 'filters' in self._context:
                filters.extend(self._context['filters'])
            ids = self.search(filters, limit=int(limit)).ids
        res = None
        try:
            # auto-commit except in testing mode
            auto_commit = not getattr(threading.currentThread(), 'testing', False)
            res = self.browse(ids).send(auto_commit=auto_commit)
        except Exception:
            _logger.exception("Failed processing mail queue")
        return res