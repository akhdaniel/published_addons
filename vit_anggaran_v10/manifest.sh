#!/usr/bin/env bash
find . -type f -name __openerp__.py -exec rename 's/__openerp__.py/__manifest__.py/' '{}' \;

