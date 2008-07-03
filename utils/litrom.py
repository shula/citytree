#!/usr/bin/env python2.4
# -*- coding: utf-8 -*-


import re

from twill.commands import *
from twill import get_browser

from litrom_settings import LITROM_PASSWORD, LITROM_USERNAME

def get_csv_html():
    b=get_browser()

    go('https://www.litrom.com/mng/')
    formvalue('1', 'U', LITROM_USERNAME)
    formvalue('1', 'P', LITROM_PASSWORD)
    submit()
    code('200')
    go('https://www.printmall.co.il/Artists/Don_TDons.asp')
    formvalue('1','SEP',',')
    submit()

    return b.get_html()

re_fields=re.compile('(?P<field>[^,]*),\s*')

def get_donors(txt):
    fields = ['handled', 'campaign', 'amount', 'date', 'first', 'last', 'address', 'city', 'mikud', 'email', 'comment']
    n = len(fields)
    lines_1 = [l for l in [l.strip() for l in txt[txt.index('>', txt.index('body'))+1:txt.index('_____')].split('\r')] if l not in ['', '<br>']]
    lines_u=[[unicode(s, 'windows-1255') for s in re.findall(re_fields, line)] for line in lines_1]
    lines = [lines_u[0], []] # header is a single line
    for line in lines_u[1:]:
        if len(lines[-1]) < n:
            lines[-1].extend(line)
        else:
            lines.append(line)
    assert(set(map(len, lines[1:])) == set([n]))
    # there may be superfluous carriage returns - count the ',' 
    #טופל  קמפיין  סכום  תאריך  שם פרטי  שם משפחה  כתובת  עיר  מיקוד  דואר אלקטרוני
    donors = [dict(zip(fields, line) + [('line', line)]) for line in lines[1:]]
    return donors
	
if __name__ == '__main__':
    output = get_csv_html()
    open('output.csv','w+').write(output)
    print output
    print get_donors(output)

