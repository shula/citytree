from django.conf import settings
from django.template import Library

register = Library()

@register.simple_tag
def YUI():
    """ return path to YUI component.
    
    Base is YUI_URL from settings or ``/yui``.
    
    Usage::
    
        {% YUI %}
    """

    return getattr(settings, 'YUI_URL', '/yui').rstrip('/')
#
