import datetime
from itertools import islice
import json
import xml.etree.ElementTree as ET

import logging
import re

import werkzeug.utils
import urllib2
import werkzeug.wrappers

import odoo
from odoo import  http
from odoo.http import request
from odoo import SUPERUSER_ID

logger = logging.getLogger(__name__)

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
        documents = http.request.env['muk_dms.file'].search([('directory','=',directory.id)])
        document_types = http.request.env['dms.document_type'].search([])

        document_type_id = int(kw.get('document_type_id',0))
        search_key = kw.get('search_key','')
        extensions = ['.pdf','.odt','.ods','.odp']

        is_login = request.env.user != request.website.user_id
        is_admin = request.env.user == SUPERUSER_ID

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

    @http.route('/dms/view/<model("muk_dms.file"):document>', type='http', auth="user", website=True)
    def view(self, document, **kw):
        values = {
            'content'   : 'view',
            'document'  : document,
        }
        return request.render('vit_dms.index', values)
