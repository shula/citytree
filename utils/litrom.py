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

re_fields=re.compile('(?P<field>[^,]+)\s*,\s*')

def get_donors(txt):
    lines = [l for l in [l.strip() for l in txt[txt.index('>', txt.index('body'))+1:txt.index('_____')].split('\r')] if l not in ['', '<br>']]
    lines_u=[[unicode(s, 'windows-1255') for s in re.findall(re_fields, line)] for line in lines]
    #טופל  קמפיין  סכום  תאריך  שם פרטי  שם משפחה  כתובת  עיר  מיקוד  דואר אלקטרוני
    fields = ['handled', 'campaign', 'amount', 'date', 'first', 'last', 'address', 'city', 'mikud', 'email']
    donors = [dict(zip(fields, line)) for line in lines_u[1:]]
    return donors
	
if __name__ == '__main__':
    output = get_csv_html()
    open('output.csv','w+').write(output)
    print output
    print get_donors(output)

