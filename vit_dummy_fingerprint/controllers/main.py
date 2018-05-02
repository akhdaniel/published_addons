import simplejson
import logging
from odoo import  http
from odoo.http import request

logger = logging.getLogger(__name__)

class BaseWebsite(http.Controller):

    @http.route('/enroll/<int:partner_id>', type='http', auth="public", website=True)
    def enroll(self, partner_id=None, **kw):
        data = {'status': 0, 
            'partner_id': partner_id,
            'message': 'Enrol succeed'}
        return simplejson.dumps(data)

    @http.route('/verify/<int:partner_id>', type='http', auth="public", website=True)
    def verify(self, partner_id=None, **kw):
        data = {'status': 0, 
            'partner_id': partner_id,
            'message': 'Verify succeed'}
        return simplejson.dumps(data)

    @http.route('/identify/<int:partner_id>', type='http', auth="public", website=True)
    def identify(self, partner_id=None, **kw):
        data = {'status': 0, 
            'partner_id': partner_id,
            'message': 'Identify succeed'}
        return simplejson.dumps(data)

