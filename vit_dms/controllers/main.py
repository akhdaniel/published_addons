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

logger = logging.getLogger(__name__)

class BaseWebsite(http.Controller):

    @http.route('/dms', type='http', auth="public", website=True)
    def index(self, **kw):
        directorates = http.request.env['hr.department'].search([])
        values = {
            'content'       : 'menu',
            'directorates'  : directorates,
        }
        return request.render('vit_dms.index', values)


    @http.route('/dms/document/<model("hr.department"):department>', type='http', auth="user", website=True)
    def document(self, department, **kw):
        documents = http.request.env['dms.document'].search([('department_id','=',department.id)])
        document_types = http.request.env['dms.document_type'].search([])

        document_type_id = int(kw.get('document_type_id',0))
        search_key = kw.get('search_key','')

        values = {
            'content'       : 'document',
            'documents'     : documents,
            'document_types': document_types,
            'document_type_id' : document_type_id,
            'department'    : department,
            'search_key'    : search_key,
        }
        return request.render('vit_dms.index', values)

    @http.route('/dms/view/<model("dms.document"):document>', type='http', auth="user", website=True)
    def view(self, document, **kw):
        values = {
            'content'   : 'view',
            'document'  : document,
        }
        return request.render('vit_dms.index', values)
