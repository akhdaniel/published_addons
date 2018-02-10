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

    @http.route('/myweb/index', type='http', auth="public", website=True)
    def index(self, **kw):
        return "index"