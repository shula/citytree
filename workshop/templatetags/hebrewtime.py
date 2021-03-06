# -*- coding: utf-8 -*-
from datetime import datetime

from django.template import Library

register = Library()

def hebrew_timeuntil(time1, time2=None):
    if time2 is None:
        time2 = datetime.now()

    d = time2 - time1
    hr = int(d.seconds/3600)
    if d.days > 0:
        return u'%s ימים ו-%s שעות' % (d.days, hr)
    if d.seconds % 3600 < 1800:
        return u'%s שעות' % hr
    return u'%s שעות וחצי' % hr

def hebrew_weekday(dt):
    # monday is 0, .., sunday is 6 - yuck
    return ['שני','שלישי','רביעי','חמישי','שישי','שבת','ראשון'][dt.weekday()]

register.filter('hebrew_timeuntil', hebrew_timeuntil)
register.filter('hebrew_weekday', hebrew_weekday)
