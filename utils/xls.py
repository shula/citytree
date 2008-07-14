#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cStringIO import StringIO
try:
    from contrib.pyExcelerator import *
except ImportError:
    import sys, os
    sys.path.append(os.path.join(os.getcwd()))
    from contrib.pyExcelerator import *

UnicodeUtils.DEFAULT_ENCODING = 'utf-8'

def tostring(sheet_name, headers, data):
    s = StringIO()
    write(sheet_name, headers, data, s)
    return s.getvalue()

def _8(x):
    if type(x) == unicode:
        x = x.encode('utf-8')
    return x

def write(sheet_name, headers, data, fd):
    w = Workbook()
    ws1 = w.add_sheet(_8(sheet_name))
    for i, h in enumerate(headers):
        ws1.write(0, i, _8(h))
    for row, l in enumerate(data):
        for col, x in enumerate(l):
            ws1.write(row+1, col, _8(x))
    w.save(fd)

if __name__ == '__main__':
    open('xls.xls','wb').write(tostring('אלון', ['אב'], [['אבגד_שלום'],[u'אבגד'],[30]]))

