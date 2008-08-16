#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-

import re
import os
from stat import ST_MTIME
from datetime import datetime

from twill.commands import *
from twill import get_browser

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
    formvalue('1', 'U', LITROM_USERNAME)
    formvalue('1', 'P', LITROM_PASSWORD)
    submit()
    code('200')
    go('https://www.printmall.co.il/Artists/Don_TDons.asp')
    formvalue('1','SEP',',')
    submit()

    data = b.get_html()
    fd = open(get_csv_html_cache, 'w+')
    fd.write(data)
    fd.close()
    return data

CITYTREE_CAMPAIGN = '266'
re_fields=re.compile('(?P<field>[^,]*),\s*')

def get_donors(txt):
    fields = ['handled', 'campaign', 'amount', 'date', 'first', 'last', 'address', 'city', 'mikud', 'email', 'comment']
    start_fields = fields[:6] # up to and including last
    n = len(fields)
    lines_1 = [l for l in [l.strip() for l in txt[txt.index('>', txt.index('body'))+1:txt.index('_____')].split('\r')] if l not in ['', '<br>']]
    lines_u=[[unicode(s, 'windows-1255') for s in re.findall(re_fields, line)] for line in lines_1]
    lines = [lines_u[0], []] # header is a single line
    for line in lines_u[1:]:
        if len(lines[-1]) < n:
            lines[-1].extend(line)
        else:
            lines.append(line)
    # there may be superfluous carriage returns - count the ',' 
    #טופל  קמפיין  סכום  תאריך  שם פרטי  שם משפחה  כתובת  עיר  מיקוד  דואר אלקטרוני
    # new tactic: the first four, handled+campaign+amount+date+first+last are always
    # there. The last (email) is always there. Everything in the middle is taken as
    # address+city+mikud, not very intelligently - we can edit it later. Nothing automatic
    # relies on it (but automatic stuff does rely on email being the actuall email address).
    donors = []
    for line in lines[1:]:
        donor = {}
        for i, f in enumerate(start_fields):
            donor[f] = line[i]
        donor['email'], donor['comment'] = line[-2:]
        mid = line[len(start_fields):len(fields)-2]
        donor['address'], donor['city'], donor['mikud'] = mid[:-2], mid[-2], mid[-1]
        donors.append(donor)
    donors = [d for d in donors if d['campaign'] == CITYTREE_CAMPAIGN]
    
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

