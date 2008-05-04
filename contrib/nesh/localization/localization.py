""" basic localization functions
    based on locale.py from python 2.4 distribution
"""

import locale, copy
import os, sys, shlex
from django.utils.translation import to_locale, get_language
from django.conf import settings

# from django.utils.translation
try:
    import threading
    hasThreads = True #IGNORE:C0103
except ImportError:
    hasThreads = False #IGNORE:C0103

if hasThreads:
    currentThread = threading.currentThread  #IGNORE:C0103
else:
    def currentThread():  #IGNORE:C0103
        """ dummy """
        return 'no threading'
#

class L10NSyntaxError(Exception):
    pass
#

def _get_paths():
    """ lifted from translation.py """
    path = []
    # global path
    path.append(os.path.join(os.path.dirname(sys.modules[settings.__module__].__file__), 'locale'))

    path.append(os.path.join(os.path.dirname(__file__), 'locale')) # add my dir
    
    # local paths
    if hasattr(settings, 'LOCALE_PATHS'):
        for localepath in settings.LOCALE_PATHS:
            if os.path.isdir(localepath):
                path.append(localepath)
    #

    # project paths
    if settings.SETTINGS_MODULE is not None:
        parts = settings.SETTINGS_MODULE.split('.')
        project = __import__(parts[0], {}, {}, [])
        path.append(os.path.join(os.path.dirname(project.__file__), 'locale'))

    path.reverse()
    return path
#

def _normalize(loc):
    """ convert django locale to locale.py name """
    return locale.normalize(to_locale(loc))
#
def _parse_line(line, n):
    try:
        return shlex.split(line, True)
    except ValueError, err:
        raise L10NSyntaxError, '%d: ERROR %s -- %s' % (n, err, line)
#

def _read_file(fh):
    """ iterator """
    while True:
        line = unicode(fh.readline(), 'utf-8')
        if not line: return
        # Ignore comments and blank lines
        if line[0] == '#' or line.strip() == '':
            continue
        nextline = line.strip()
        # Join continuation lines
        while nextline.endswith('\\'):
            nextline = unicode(fh.readline().strip(), 'utf-8').strip()
            if not nextline: nextline = ''
            line = line + nextline
        #
        yield line.strip().encode('utf-8')
    #
#

class Locale(object):
    """ load and hold locale information """
    
    def __init__(self, loc):
        super(Locale, self).__init__()
        self._loc_info = {}

        if loc not in ('C', 'POSIX'):
            self.locale = to_locale(loc)
            self._load_locale(loc)
        #
        
        if not len(self._loc_info):
            self._fallback(loc)
            # final fallback
            if not len(self._loc_info):
                self._fallback('C')
            #
        #
    #
    
    LC_NUMERIC = (
                  'decimal_point',
                  'thousands_sep',
                  'grouping',
                  )
    def _load_numeric(self, path):
        fh = file(path, 'rU')

        line = fh.readline().strip()
        
        if line != 'LC_NUMERIC':
            raise L10NSyntaxError, 'invalid file header (%r)' % line
        #
        
        n = 0
        for line in _read_file(fh):
            n += 1

            if line.startswith('END'):
                return
            
            # TODO: copy
            kw, val = _parse_line(line, n)
            if kw not in Locale.LC_NUMERIC:
                raise L10NSyntaxError, '%d: ERROR unknown keyword %r' % (n, kw)
            
            try:
                if kw == 'grouping':
                    if ';' in val: # XXX semicolon ?
                        val = [int(x) for x in val.split(';')]
                    else:
                        val = [int(val)]
                    #
                #
            except ValueError, err:
                raise L10NSyntaxError, '%d: ERROR %s' % (n, err)
            #
            
            if 'LC_NUMERIC' not in self._loc_info:
                self._loc_info['LC_NUMERIC'] = {}
            #
            if 'LC_MONETARY' not in self._loc_info:
                self._loc_info['LC_MONETARY'] = {}
            #
            
            self._loc_info['LC_MONETARY'][kw] = self._loc_info['LC_NUMERIC'][kw] = val
        # for
    #
    
    def _load_monetary(self, path):
        pass
    #
    
    LC_TIME = (
                  'd_t_fmt',
                  'd_fmt',
                  't_fmt',
                  'am_pm',
                  'am_pm',
                  't_fmt_ampm',
                  'day',
                  'abday',
                  'mon',
                  'abmon',
                  'era',
                  'era_d_fmt',
                  'era_t_fmt',
                  'era_d_t_fmt',
                  'alt_digits',
                  )
    
    def _load_time(self, path):
        fh = file(path, 'rU')

        line = fh.readline().strip()
        
        if line != 'LC_TIME':
            raise L10NSyntaxError, 'invalid file header (%r)' % line
        #
        
        n = 0
        for line in _read_file(fh):
            n += 1

            if line.startswith('END'):
                return
            
            # TODO: copy
            print >> sys.stderr, line
            kw, val = _parse_line(line, n)
            print >> sys.stderr, kw, val
            
            if kw not in Locale.LC_TIME:
                raise L10NSyntaxError, '%d: ERROR unknown keyword %r' % (n, kw)
            
            try:
                if kw == 'grouping':
                    if ';' in val: # XXX semicolon ?
                        val = [int(x) for x in val.split(';')]
                    else:
                        val = [int(val)]
                    #
                #
            except ValueError, err:
                raise L10NSyntaxError, '%d: ERROR %s' % (n, err)
            #
            
            if 'LC_TIME' not in self._loc_info:
                self._loc_info['LC_TIME'] = {}
            #
            
            self._loc_info['LC_TIME'][kw] = self._loc_info['LC_TIME'][kw] = val
        # for
    #
    
    def _load_locale(self, loc):
        """ load and parse LC_* files """
        
        for path in _get_paths():
            base = os.path.join(path, loc)
            # well, switch ;)
            if os.path.isfile(os.path.join(base, 'LC_NUMERIC')):
                self._load_numeric(os.path.join(base, 'LC_NUMERIC'))

            if os.path.isfile(os.path.join(base, 'LC_MONETARY')):
                self._load_monetary(os.path.join(base, 'LC_MONETARY'))

            if os.path.isfile(os.path.join(base, 'LC_TIME')):
                self._load_time(os.path.join(base, 'LC_TIME'))
            #
        #
    #
    
    def _fallback(self, loc):
        # Fallback to system locale
        l10n = {}
        
        # TIME
        old = locale.setlocale(locale.LC_TIME)
        l10n['LC_TIME'] = {}
        try:
            locale.setlocale(locale.LC_TIME, _normalize(loc))
        except locale.Error:
            return
        #
        
        try:
            for what in (
                         locale.D_T_FMT, locale.D_FMT, locale.T_FMT, locale.T_FMT_AMPM,
                         locale.DAY_1, locale.DAY_2, locale.DAY_3, locale.DAY_4,
                         locale.DAY_5, locale.DAY_6, locale.DAY_7,
                         locale.ABDAY_1, locale.ABDAY_2, locale.ABDAY_3, locale.ABDAY_4,
                         locale.ABDAY_5, locale.ABDAY_6, locale.ABDAY_7, 
                         locale.MON_1, locale.MON_2, locale.MON_3, locale.MON_4,
                         locale.MON_5, locale.MON_6, locale.MON_7, locale.MON_8,
                         locale.MON_9, locale.MON_10, locale.MON_11, locale.MON_12, 
                         locale.ABMON_1, locale.ABMON_2, locale.ABMON_3, locale.ABMON_4,
                         locale.ABMON_5, locale.ABMON_6, locale.ABMON_7, locale.ABMON_8,
                         locale.ABMON_9, locale.ABMON_10, locale.ABMON_11, locale.ABMON_12, 
                         locale.ERA, locale.ERA_D_T_FMT, locale.ERA_D_FMT,
                         ):
                l10n['LC_TIME'][what] = l10n[what] = locale.nl_langinfo(what)
            #
        finally:
            locale.setlocale(locale.LC_TIME, old)
        #
        
        # numbers
        # TIME
        old = locale.setlocale(locale.LC_NUMERIC)
        l10n['LC_NUMERIC'] = {}
        l10n['LC_MONETARY'] = {}
        
        try:
            locale.setlocale(locale.LC_NUMERIC, _normalize(loc))
        except locale.Error:
            return
        #
    
        try:
            l10n['LC_MONETARY'] = locale.localeconv()
            for what in (locale.ALT_DIGITS, locale.RADIXCHAR, locale.THOUSEP):
                l10n['LC_MONETARY'][what] = l10n[what] = locale.nl_langinfo(what)
        finally:
            locale.setlocale(locale.LC_NUMERIC, old)
        #
        l10n['LC_NUMERIC']['decimal_point'] = l10n['LC_MONETARY']['decimal_point'] 
        l10n['LC_NUMERIC']['thousands_sep'] = l10n['LC_MONETARY']['thousands_sep']
        l10n['LC_NUMERIC']['grouping'] = l10n['LC_MONETARY']['grouping']
        #
        
        self._loc_info = copy.deepcopy(l10n) # XXX Is this is really needed?
    #
    
    def localeconv(self):
        """ localeconv() -> dict.
            Returns numeric and monetary locale-specific parameters.
        """
        
        return self._loc_info.get('LC_MONETARY', {})
    #
    
    def nl_langinfo(self, what):
        """ return locale information """
        
        return self._loc_info.get(what, None)
    #
# Locale


class Localization(object):
    """ localization storage """
    def __init__(self):
        super(Localization, self).__init__()
        self.locales = {}
        self._active = {}
    #

    def set_localization(self, loc, val):
        """ store localization info in cache """
        self.locales[loc] = val
    #
    def get_localization(self, loc):
        """ get localization info from cache """
        return self.locales.get(loc, None)
    #

    def _set_active(self, val):
        """ property access """
        self._active[currentThread()] = val
    #
    def _get_active(self):
        """ property access """
        act = self._active.get(currentThread(), None)
        if act is None:
            self._active[currentThread()] = localization('C') # default
        #
        return self._active[currentThread()]
    #
    active = property(fget=_get_active, fset=_set_active)
#
_L10N = Localization() #IGNORE:C0103


def localization(loc):
    """ load and return localization data """
    t = _L10N.get_localization(loc)
    if t is not None:
        return t
    #
    l = Locale(loc)
    _L10N.set_localization(loc, l) # cache
    return l
#

def setlocale(loc=None):
    """ load and set current locale """
    if loc is None:
        loc = get_language()
    #
    _L10N.active = localization(loc)
#

def localeconv():
    """ localeconv() -> dict.
        Returns numeric and monetary locale-specific parameters.
    """
    return _L10N.active.localeconv()
#

def nl_langinfo(what):
    """ return locale information """
    return _L10N.active.nl_langinfo(what)
#

### Number formatting APIs -- from locale.py

# Author: Martin von Loewis

def _group(data):
    """ perform the grouping from right to left """
    
    conv = localeconv()
    grouping = conv['grouping']
    if not grouping:
        return (data, 0)
    result = ""
    seps = 0
    spaces = ""
    if data[-1] == ' ':
        sp_pos = data.find(' ')
        spaces = data[sp_pos:]
        data = data[:sp_pos]
    while data and grouping:
        # if grouping is -1, we are done
        if grouping[0] == locale.CHAR_MAX:
            break
        # 0: re-use last group ad infinitum
        elif grouping[0] != 0:
            #process last group
            group = grouping[0]
            grouping = grouping[1:]
        if result:
            result = data[-group:] + conv['thousands_sep'] + result
            seps += 1
        else:
            result = data[-group:]
        data = data[:-group]
        if data and data[-1] not in "0123456789":
            # the leading string is only spaces and signs
            return data + result + spaces, seps
    if not result:
        return data + spaces, seps
    if data:
        result = data + conv['thousands_sep'] + result
        seps += 1
    return result + spaces, seps

def format(format_str, val, grouping=0):
    """Formats a value in the same way that the % formatting would use,
    but takes the current locale into account.
    Grouping is applied if the third parameter is true."""
    result = format_str % val
    fields = result.split(".")
    seps = 0
    if grouping:
        fields[0], seps = _group(fields[0])
    if len(fields) == 2:
        result = fields[0] + localeconv()['decimal_point'] + fields[1]
    elif len(fields) == 1:
        result = fields[0]
    else:
        raise locale.Error, "Too many decimal points in result string"

    while seps:
        # If the number was formatted for a specific width, then it
        # might have been filled with spaces to the left or right. If
        # so, kill as much spaces as there where separators.
        # Leading zeroes as fillers are not yet dealt with, as it is
        # not clear how they should interact with grouping.
        sp_pos = result.find(" ")
        if sp_pos == -1:
            break
        result = result[:sp_pos] + result[sp_pos + 1:]
        seps -= 1

    return result

def str(val): #IGNORE:W0622 -- intentional
    """Convert float to integer, taking the locale into account."""
    return format("%.12g", val)

def atof(string, func=float):
    "Parses a string as a float according to the locale settings."
    #First, get rid of the grouping
    t_sep = localeconv()['thousands_sep']
    if t_sep:
        string = string.replace(t_sep, '')
    #next, replace the decimal point with a dot
    d_point = localeconv()['decimal_point']
    if d_point:
        string = string.replace(d_point, '.')
    #finally, parse the string
    return func(string)

def atoi(string):
    "Converts a string to an integer according to the locale settings."
    return atof(string, int)
