from django.template import Node
from django.template import TemplateSyntaxError, Library
from nesh.news.models import Entry

register = Library()

class GetNewsNode(Node):
    def __init__(self, variable, max=10):
        self.variable = variable
        self.max = max

    def render(self, context):
        context[self.variable] = Entry.objects.get_news(self.max)
        return ''
#

def do_get_news(parser, token):
    """
    This will store a list of the news
    in the context.

    Usage::

        {% get_news as news_list max 5 %}
        {% for news in news_list %}
        ...
        {% endfor %}
    """

    args = token.contents.split()
    
    if len(args) == 5:
        if (not args[1] == 'as') and (not args[5] == 'max'):
            raise TemplateSyntaxError, "'get_news' requires 'as and max variables' (got %r)" % args
        try:
            max = int(args[4])
        except ValueError, err:
            raise TemplateSyntaxError, "'get_news' requires 'max' to be a valid integer (got %r): %s" % (args[4], err)
            
        return GetNewsNode(args[2], max)
    elif len(args) != 3 or args[1] != 'as':
        raise TemplateSyntaxError, "'get_news' requires 'as variable' (got %r)" % args
    #
    return GetNewsNode(args[2])
#

register.tag('get_news', do_get_news)