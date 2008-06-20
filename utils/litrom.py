#!/usr/bin/env python2.4

from twill.commands import *
from twill import get_browser

from litrom_settings import LITROM_PASSWORD, LITROM_USERNAME

def get_csv():
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

if __name__ == '__main__':
    output = get_csv()
    open('output.csv','w+').write(output)
    print output
