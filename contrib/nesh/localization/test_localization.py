# -*- coding: utf-8 -*-
# pylint: disable-msg=W0403,W0603,C0111,C0103,W0142,C0301
""" partialy stolen from python locale tests ;)
    requires nose (easy_install nose)
    nosetests -v --with-coverage --cover-package=localization test_localization.py
"""

from django.conf import settings
settings.configure(DEBUG=True,
                   )
import nose
import locale
import sys
from localization import (setlocale, format, atoi, atof, _normalize,
                          nl_langinfo, localeconv)

OLD_LOCALE_TM = None
def setup_tm():
    """ setup for date/time tests """
    global OLD_LOCALE_TM
    OLD_LOCALE_TM = locale.setlocale(locale.LC_TIME)
#

def tear_down_tm():
    """ cleanup for date/time tests """
    locale.setlocale(locale.LC_TIME, OLD_LOCALE_TM)
#

OLD_LOCALE_NUM = None
def setup_num():
    """ setup for numeric tests """
    global OLD_LOCALE_NUM
    OLD_LOCALE_NUM = locale.setlocale(locale.LC_NUMERIC)
#

def tear_down_num():
    """ cleanup for numeric tests """
    locale.setlocale(locale.LC_NUMERIC, OLD_LOCALE_NUM)
#

# setup locale list and ensure that C and en comes first
CANDIDATE_LOCALES = [x[0] for x in [('C', 1), ('en', 1)]]# + list(settings.LANGUAGES)]

OLD_LOCALE_NUM = locale.setlocale(locale.LC_NUMERIC)

if sys.platform.startswith("win"):
    locale.setlocale(locale.LC_NUMERIC, "en")
elif sys.platform.startswith("freebsd"):
    locale.setlocale(locale.LC_NUMERIC, "en_US.US-ASCII")
else:
    locale.setlocale(locale.LC_NUMERIC, "en_US")
#

# BASE FUNCTIONALITY

def test_number_format():
    setlocale('en')

    td = (
          # w/o grouping
          (("%f", 1024), '1024.000000'),
          (("%f", 102), '102.000000'),
          (("%f", -42), '-42.000000'),
          (("%+f", -42), '-42.000000'),
          (("%20.f", -42), '                 -42'),
          (("%+10.f", -4200), '     -4200'),
          (("%-10.f", 4200),'4200      '),

          # with grouping
          (("%f", 1024, 1), '1,024.000000'),
          (("%f", 102, 1), '102.000000'),
          (("%f", -42, 1), '-42.000000'),
          (("%+f", -42, 1), '-42.000000'),
          (("%20.f", -42, 1), '                 -42'),
          (("%+10.f", -4200, 1), '    -4,200'),
          (("%-10.f", 4200, 1),'4,200     '),
          )
    
    for args, res in td:
        assert format(*args) == res, '%r != %r' % (format(*args), res)
#



def _set_locale(what, loc):
    try:
        locale.setlocale(what, loc)
    except locale.Error:
        locale.setlocale(what, '')
#

@nose.with_setup(setup_num, tear_down_num)
def test_conversion():
    setlocale('en')
    
    # INT
    val = 123456789

    s1 = format("%d", 123456789, 1)
    assert s1 == '123,456,789', '%r != %r' % (val, s1)
    assert val == atoi(s1), '%r != %r' % (val, atoi(s1))

    # FLOAT
    val = 123456789.14
    s1 = str(val)
    s2 = format("%.2f", val, 1)
    assert s2 == '123,456,789.14', '%r != %r' % (val, s2)
    assert val == atof(s1), '%r != %r' % (val, atof(s1))
#

@nose.with_setup(setup_num, tear_down_num)
def test_numeric():
    for loc in CANDIDATE_LOCALES:
        lc_norm = _normalize(loc)
        _set_locale(locale.LC_NUMERIC, lc_norm)
        setlocale(loc)
        # short
        for what in (locale.ALT_DIGITS, locale.RADIXCHAR, locale.THOUSEP):
            nl = nl_langinfo(what)
            lo = locale.nl_langinfo(what)
            assert nl == lo, '%s (%s): %r != %r' % (loc, lc_norm, nl, lo)
        #
    # for
#

@nose.with_setup(setup_num, tear_down_num)
def test_monetary():
    for loc in CANDIDATE_LOCALES:
        lc_norm = _normalize(loc)
        _set_locale(locale.LC_NUMERIC, lc_norm)
        setlocale(loc)
        # short
        nl = locale.localeconv()
        li = localeconv()
        for k, v in nl.items():
            assert v == li[k], '%s (%s): %s %r != %r' % (loc, lc_norm, k, v, li[k])
        #
    # for
#

@nose.with_setup(setup_tm, tear_down_tm)
def test_date_time_format():
    for loc in CANDIDATE_LOCALES:
        lc_norm = _normalize(loc)
        _set_locale(locale.LC_TIME, lc_norm)
        setlocale(loc)
        for what in (
                     locale.D_T_FMT, locale.D_FMT, locale.T_FMT, locale.T_FMT_AMPM,
                     ):
            nl = nl_langinfo(what)
            lo = locale.nl_langinfo(what)
            assert nl == lo, '%r != %r' % (nl, lo)
        #
    #
#

@nose.with_setup(setup_tm, tear_down_tm)
def test_day_names():
    for loc in CANDIDATE_LOCALES:
        lc_norm = _normalize(loc)
        _set_locale(locale.LC_TIME, lc_norm)
        setlocale(loc)
        for what in (
                     locale.DAY_1, locale.DAY_2, locale.DAY_3, locale.DAY_4, locale.DAY_5, locale.DAY_6, locale.DAY_7,
                     locale.ABDAY_1, locale.ABDAY_2, locale.ABDAY_3, locale.ABDAY_4, locale.ABDAY_5, locale.ABDAY_6, locale.ABDAY_7, 
                     ):
            nl = nl_langinfo(what)
            lo = locale.nl_langinfo(what)
            assert nl == lo, '%r != %r' % (nl, lo)
        #
    #
#

@nose.with_setup(setup_tm, tear_down_tm)
def test_month_names():
    for loc in CANDIDATE_LOCALES:
        lc_norm = _normalize(loc)
        _set_locale(locale.LC_TIME, lc_norm)
        setlocale(loc)
        for what in (
                     locale.MON_1, locale.MON_2, locale.MON_3, locale.MON_4, locale.MON_5, locale.MON_6, locale.MON_7, locale.MON_8, locale.MON_9, locale.MON_10, locale.MON_11, locale.MON_12, 
                     locale.ABMON_1, locale.ABMON_2, locale.ABMON_3, locale.ABMON_4, locale.ABMON_5, locale.ABMON_6, locale.ABMON_7, locale.ABMON_8, locale.ABMON_9, locale.ABMON_10, locale.ABMON_11, locale.ABMON_12, 
                     ):
            nl = nl_langinfo(what)
            lo = locale.nl_langinfo(what)
            assert nl == lo, '%r != %r' % (nl, lo)
        #
    #
#

@nose.with_setup(setup_tm, tear_down_tm)
def test_era():
    for loc in CANDIDATE_LOCALES:
        lc_norm = _normalize(loc)
        _set_locale(locale.LC_TIME, lc_norm)
        setlocale(loc)
        for what in (
                     locale.ERA, locale.ERA_D_T_FMT, locale.ERA_D_FMT,
                     ):
            nl = nl_langinfo(what)
            lo = locale.nl_langinfo(what)
            assert nl == lo, '%r != %r' % (nl, lo)
        #
    #
#

def test_sr_number_format():
    setlocale('sr')

    td = (
          # w/o grouping
          (("%f", 1024), '1024,000000'),
          (("%f", 102), '102,000000'),
          (("%f", -42), '-42,000000'),
          (("%+f", -42), '-42,000000'),
          (("%20.f", -42), '                 -42'),
          (("%+10.f", -4200), '     -4200'),
          (("%-10.f", 4200),'4200      '),

          # with grouping
          (("%f", 1024, 1), '1.024,000000'),
          (("%f", 102, 1), '102,000000'),
          (("%f", -42, 1), '-42,000000'),
          (("%+f", -42, 1), '-42,000000'),
          (("%20.f", -42, 1), '                 -42'),
          (("%+10.f", -4200, 1), '    -4.200'),
          (("%-10.f", 4200, 1),'4.200     '),
          )
    
    for args, res in td:
        assert format(*args) == res, '%r != %r' % (format(*args), res)
#

# DJANGO FUNCTIONALITY

# FIXME: specific number and date/time tests
