#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

import re
import os
from stat import ST_MTIME
from datetime import datetime

from twill.commands import *
from twill import get_browser
from twill.errors import TwillException

from litrom_settings import LITROM_PASSWORD, LITROM_USERNAME

get_csv_html_cache = '%s/.litrom_csv_html' % os.environ['HOME']
cache_hours = 1
def file_newness_in_hours(f):
    dt = datetime.now() - datetime.fromtimestamp(os.stat(f)[ST_MTIME])
    return dt.days*24 + int(dt.seconds/3600)

def get_csv_html():
    if os.path.exists(get_csv_html_cache)\
        and file_newness_in_hours(get_csv_html_cache) < cache_hours:
        return open(get_csv_html_cache).read()

    b=get_browser()

    go('https://www.litrom.com/mng/')
    done = False
    tries = 4
    while not done and tries > 0:
        tries -= 1
        try:
            formvalue('1', 'U', LITROM_USERNAME)
            formvalue('1', 'P', LITROM_PASSWORD)
            submit()
        except TwillException, e:
            pass
        code('200')
        go('https://www.litrom.com/my/Don_TDons_REP.asp')
        go('https://www.litrom.com/my/Don_TXTRep_Excel.asp')
        done = True
    assert(done)

    data = b.get_html()
    fd = open(get_csv_html_cache, 'w+')
    fd.write(data)
    fd.close()
    return data

CITYTREE_CAMPAIGN = '266'
re_fields=re.compile('(?P<field>[^,]*),\s*')

def get_donors(txt):
    from BeautifulSoup import BeautifulSoup
    soup = BeautifulSoup(txt)
    fields = ['action_number', 'handled', 'campaign', 'amount', 'date', 'first', 'last', 'address', 'city', 'mikud', 'email', 'comment']
    # [1:] - remove header
    donors = [dict(zip(fields, [d.string for d in r.findAll('td')])) for r in soup.body.table.findAll('tr')[1:]]
    return donors
	
if __name__ == '__main__':
    import os
    output_filename = 'output.csv'
    if not os.path.exists(output_filename):
        output = get_csv_html()
        open(output_filename, 'w+').write(output)
    else:
        output = open(output_filename).read()
    print output
    print '\n'.join(map(str,get_donors(output)))

