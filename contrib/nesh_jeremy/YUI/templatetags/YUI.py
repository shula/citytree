from django.conf import settings
from django.template import Library

register = Library()

@register.simple_tag
def YUI(what):
    """ return path to YUI component.
    
    Base is YUI_URL from settings or ``/yui``.
    
    Usage::
    
        {% YUI what %}
    """

    if '/' in what:
        dir, name = what.rsplit('/')
        dir += '/'
    else:
        dir = ''
        name = what
    if '.' in what:
        name, ext = name.split('.')
        name = name.strip()
    else:
        name = name.strip()
        ext = 'js'
    if ext == 'js':
        fname = dir + name + '-min.' + ext
    else:
        fname = dir + name + '.' + ext
    #version = settings.DEBUG and 'debug' or 'min'
    ext = ext.strip()
    return '%s/%s/%s' % (
                          getattr(settings, 'YUI_URL', '/yui'),
                          name,
                          fname
                          )
#
