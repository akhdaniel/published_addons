import datetime
from itertools import islice
import json
import xml.etree.ElementTree as ET
import functools
import time
import logging
import re
from odoo import _

import werkzeug.utils
import urllib2
import werkzeug.wrappers

import odoo
from odoo import  http
from odoo.http import request
from odoo import SUPERUSER_ID
from odoo.http import content_disposition, dispatch_rpc, request, \
                      serialize_exception as _serialize_exception
import base64
from odoo.exceptions import AccessError

_logger = logging.getLogger(__name__)

def serialize_exception(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception, e:
            _logger.exception("An exception occured during an http request")
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            return werkzeug.exceptions.InternalServerError(json.dumps(error))
    return wrap

class BaseWebsite(http.Controller):

    @http.route('/dms', type='http', auth="public", website=True)
    def index(self, **kw):
        directories = http.request.env['muk_dms.directory'].search([('is_root_directory','=',False)])
        values = {
            'content'       : 'menu',
            'directories'  : directories,
        }
        return request.render('vit_dms.index', values)

    @http.route('/dms/document/<model("muk_dms.directory"):directory>', type='http', auth="public", website=True)
    def document(self, directory, **kw):

        domain = [('directory','=',directory.id)]
        document_type_id = int(kw.get('document_type_id',0))
        search_key = kw.get('search_key','')

        if document_type_id != 0:
            domain.append(('document_type_id','=', document_type_id))

        if search_key !='':
            domain.append('|')
            domain.append('|')
            domain.append(('name','ilike',search_key))
            domain.append(('index_content','ilike',search_key))
            domain.append(('description','ilike',search_key))


        documents = http.request.env['muk_dms.file'].search(domain)
        document_types = http.request.env['dms.document_type'].search([])

        extensions = ['.pdf','.odt','.ods','.odp']

        is_login = request.env.user != request.website.user_id
        is_admin = request.env.user.id == SUPERUSER_ID

        values = {
            'content'       : 'document',
            'documents'     : documents,
            'document_types': document_types,
            'document_type_id' : document_type_id,
            'directory'    : directory,
            'search_key'    : search_key,
            'extensions'    : extensions,
            'is_login'      : is_login,
            'is_admin'      : is_admin,
        }
        return request.render('vit_dms.index', values)

    #@http.route('/dms/view/<model("muk_dms.file"):document>', type='http', auth="user", website=True)
    #def view(self, document, **kw):
    #    values = {
    #        'content'   : 'view',
    #        'document'  : document,
    #    }
    #    return request.render('vit_dms.index', values)

    @http.route('/dms/upload', type='http', auth="user")
    @serialize_exception
    def upload(self, **kw):
        directory_id = kw.get('directory_id',False)
        document_type_id = kw.get('document_type_id',False)
        file = kw.get('file',False)
        callback = kw.get('callback',False)

        Model = request.env['muk_dms.file']
        out = """<script language="javascript" type="text/javascript">
                    var win = window.top.window;
                    win.jQuery(win).trigger(%s, %s);
                </script>"""
        try:
            doc = Model.create({
                'name': file.filename,
                'content': base64.encodestring(file.read()),
                'title': file.filename,
                'directory': int(directory_id),
                'document_type_id': int(document_type_id),
                'date_start': time.strftime("%Y-%m-%d"),
                'date_end': time.strftime("%Y-%m-%d"),
            })
            args = {
                'filename': file.filename,
                'mimetype': file.content_type,
                'id':  doc.id
            }
        except Exception:
            args = {'error': _("Something horrible happened")}
            _logger.exception("Fail to upload attachment %s" % file.filename)
        return out % (json.dumps(callback), json.dumps(args))