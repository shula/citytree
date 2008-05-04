from django.template import Library
from nesh.articles.models import ArticleCategory, Article

register = Library()

def render_menu(top):
    ret = ['<ul>']
    
    for lnk, sub in top:
        ret.append('<li><a href="%s">%s</a></li>' % lnk)
        
        if len(sub):
            ret += render_menu(sub)
        #
    #
    
    ret.append('</ul>')
    return ret
#

@register.simple_tag
def category_menu():
    lst = ArticleCategory.objects.make_list()
    return '\n'.join(render_menu(lst))
#

@register.simple_tag
def article_menu(category):
    lst = Article.objects.make_list(category)

    if not len(lst):
        return ''
    
    ret = ['<ul>']
    
    for lnk in lst:
        ret.append('<li><a href="%s">%s</a></li>' % lnk)
    #
    
    ret.append('</ul>')

    return '\n'.join(ret)
#