from django.conf import settings
from django.template import (
                             TemplateSyntaxError, 
                             Library, 
                             Node, 
                             )

register = Library()

def _group(s, grouping=(3, 0), thousands_sep=','):
    if not grouping:return (s, 0)
    result=""
    seps = 0
    spaces = ""
    if s[-1] == ' ':
        sp = s.find(' ')
        spaces = s[sp:]
        s = s[:sp]
    while s and grouping:
        # if grouping is -1, we are done
        if grouping[0]== -1:
            break
        # 0: re-use last group ad infinitum
        elif grouping[0]!=0:
            #process last group
            group=grouping[0]
            grouping=grouping[1:]
        if result:
            result = s[-group:] + thousands_sep +result
            seps += 1
        else:
            result=s[-group:]
        s=s[:-group]
        if s and s[-1] not in "0123456789":
            # the leading string is only spaces and signs
            return s + result + spaces, seps
    if not result:
        return s+spaces,seps
    if s:
        result=s + thousands_sep + result
        seps += 1
    return result + spaces, seps
#

def format(f, val, decimal_point='.', grouping=True):
    """Formats a value in the same way that the % formatting would use,
    but takes the current locale into account.
    Grouping is applied if the grouping parameter is true."""
    if decimal_point == '.':
        thousands_sep = ','
    else:
        thousands_sep = '.'
    result = f % val
    fields = result.split(".")
    seps = 0
    if grouping:
        fields[0], seps = _group(fields[0], thousands_sep=thousands_sep)
    if len(fields) == 2:
        result = fields[0] + decimal_point + fields[1]
    elif len(fields) == 1:
        result = fields[0]
    else:
        raise ValueError, "Too many decimal points in result string"

    while seps:
        # If the number was formatted for a specific width, then it
        # might have been filled with spaces to the left or right. If
        # so, kill as much spaces as there where separators.
        # Leading zeroes as fillers are not yet dealt with, as it is
        # not clear how they should interact with grouping.
        sp = result.find(" ")
        if sp==-1:break
        result = result[:sp] + result[sp + 1:]
        seps -= 1

    return result
#
@register.simple_tag
def formatmoney(fmt, val, decimal_point='.'):
    return format(fmt, val, decimal_point=decimal_point)

@register.simple_tag
def module_name(module):
    """ returns module name """
    return module._meta.module_name

@register.simple_tag
def MEDIA_URL():
    """ return MEDIA_URL """
    return settings.MEDIA_URL.rstrip('/')

@register.simple_tag
def ADMIN_MEDIA_URL():
    """ return ADMIN_MEDIA_PREFIX """
    return settings.ADMIN_MEDIA_PREFIX.rstrip('/')

#class GetSettings(Node):
#    def __init__(self, variable):
#        super(GetSettings, self).__init__()
#        self.variable = variable
#
#    def render(self, context):
#        return getattr(settings, self.variable)
#
#@register.tag(name="get_settings")
#def get_settings(parser, token):
#    """ return value from django settings """
#
#    args = token.contents.split()
#    
#    if len(args) != 2 :
#        raise TemplateSyntaxError, "'get_settings' requires only variable name (got %r)" % args
#    if not hasattr(settings, args[1]):
#        raise TemplateSyntaxError, "'get_settings' invalid variable name for %s" % args[1]
#    return GetSettings(args[1])
