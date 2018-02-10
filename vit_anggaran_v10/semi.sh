#!/usr/bin/env bash
# pool -> env
find . -type f -name '*.py' | xargs gsed -i -e 's/self.pool/self.env/g'
# remove cr, uid
find . -type f -name '*.py' | xargs gsed -i -e 's/(cr, [^,]*, /(/g'
find . -type f -name '*.py' | xargs gsed -i -e 's/(self, cr, [^,]*, ids/(self/g'
find . -type f -name '*.py' | xargs gsed -i -e 's/(self, cr, uid, /(self, /g'
find . -type f -name '*.py' | xargs gsed -i -e 's/, context=[^,)]*//g'
find . -type f -name '*.py' | xargs gsed -i -e 's/self.env.get(\([^)]*\))/self.env[\1]/g'
# res_config.py
find . -type f -name 'res_config.py' | xargs gsed -i -e 's/\(def get_default_.*\)(self)/\1(self, fields)/g'
