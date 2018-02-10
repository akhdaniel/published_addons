#!/usr/bin/env bash
# IMPORTS
# replace osv, orm
find . -type f -name '*.py' | xargs gsed -i -e  's/from openerp.osv import orm$/from odoo import models/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/from openerp.models.orm import Model$/from odoo.models import Model/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/osv.osv_memory/models.TransientModel/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/osv.osv/models.Model/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/osv.except_osv/UserError/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/osv\./models./g'
find . -type f -name '*.py' | xargs gsed -i -e  's/\<orm\./models./g'
find . -type f -name '*.py' | xargs gsed -i -e  's/\(import .*\), osv/\1, models/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/\(import .*\)osv, /\1models, /g'
find . -type f -name '*.py' | xargs gsed -i -e  's/\(import .*\)osv/\1models/g'

find . -type f -name '*.py' | xargs gsed -i -e  's/\(import .*\), orm/\1/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/\(import .*\)orm, /\1/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/^.*import orm$//g'

find . -type f -name '*.py' | xargs gsed -i -e  's/openerp.osv/openerp/g'

# replace http import
find . -type f -name '*.py' | xargs gsed -i -e  's/from openerp.addons.web import http/from odoo import http/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/openerp.addons.web.http/odoo.http/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/openerp.http/odoo.http/g'

# replace odoo
# fix importing. Otherwise you will get error:
#   AttributeError: 'module' object has no attribute 'session_dir'
find . -type f -name '*.py' | xargs gsed -i -e  's/openerp.tools.config/odoo.tools.config/g'

# general replacement
find . -type f -name '*.py' | xargs gsed -i -e  's/from openerp/from odoo/g'


# FIELDS
# update fields
# (multiline: http://stackoverflow.com/questions/1251999/how-can-i -e -replace-a-newline-n-using-gsed/7697604#7697604 )
# delete _columns
find . -type f -name '*.py' | xargs perl -i -p0e 's/\s+_columns\s+=\s+{(.*?)\n\s+}/$1\n/gs'
# computed fields
find . -type f -name '*.py' | xargs gsed -i -e  's/fields.function(\(.*\) \(["\x27][^,]*\)/fields.function(\1 string=\2/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/fields.function(\(.*\) multi=[^,)]*/fields.function(\1/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/fields.function(\([^,]*\)\(.*\)type=.\([2a-z]*\)["\x27]/fields.\3(compute="\1"\2/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/fields.many2one(\(.*\)obj=\([^,]*\)/fields.many2one(\2, \1/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/,[ ]*,/,/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/,[ ]*,/,/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/,[ ]*,/,/g'

# replace fields
find . -type f -name '*.py' | xargs perl -i  -p0e 's/\s+_columns\s+=\s+{(.*?)\s+}/$1/gs'
find . -type f -name '*.py' | xargs gsed -i -e  's/fields\.\(.\)/fields.\u\1/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/[[:space:]]*[\x27\"]\(.*\)[\x27\"][[:space:]]*:[[:space:]]*\(fields.*\),$/\t\t\1 = \2/g'

# renamed attributes
find . -type f -name '*.py' | xargs gsed -i -e  's/select=/index=/g'
find . -type f -name '*.py' | xargs gsed -i -e  's/digits_compute=/digits=/g'
