from django import template
from citytree.cityblog.models import post
from citytree.utils.imgUtils  import replacePostImages
from django.conf import settings 
import re

register = template.Library()

def nthitem(value, arg):
    "splits it's argument by , and returns the nth item from it, 1-based"
    lst = arg.split(',')
    return lst[int(value)-1]
    
def lessthan( value, arg ):
    """returns true if value is less than argument, false otherwise"""
    num = int(arg)
    return value < num
    
def replaceMediaUrl(value, arg):
    """
    Switches all instances of {{media_url}} with settings: media url
    """
    media_url_pattern = re.compile(r'{{media_url}}', re.IGNORECASE)
    
    ret = re.sub(media_url_pattern, settings.MEDIA_URL+arg, value )
    
    return ret
    
    
    
def replacePostImagesArticle( value, arg ):
    """
    replace values of type [IMG n] with the relevant image from the post.

    usage: {{value|replacePostImagesArticle:"PostID"}}
    """
    
    try:
        postId = int(arg) # convert all ints
    except ValueError:
       raise template.TemplateSyntaxError, "replacePostImagesArticle filter: argument %r is invalid integer" % (arg)

    return replacePostImages( value, postId, 'cityblog/articleImgTemplate.html')
    

def replacePostImagesGallery( value, arg ):
    """
    replace values of type [IMG n] with the relevant image from the post.

    usage: {{value|replacePostImagesGallery:"PostID"}}
    """
    
    try:
        postId = int(arg) # convert all ints
    except ValueError:
       raise template.TemplateSyntaxError, "replacePostImagesGallery filter: argument %r is invalid integer" % (arg)

    return replacePostImages( value, int(arg), 'cityblog/galleryImgTemplate.html')
    

    
def paginator(context, adjacent_pages=2):
    """
    To be used in conjunction with the object_list generic view.

    Adds pagination context variables for use in displaying first, adjacent and
    last page links in addition to those created by the object_list generic
    view.
    """
    page_numbers = [n for n in \
                    range(context["page"] - adjacent_pages, context["page"] + adjacent_pages + 1) \
                    if n > 0 and n <= context["pages"]]
    return {
        "hits": context["hits"],
        "results_per_page": context["results_per_page"],
        "page": context["page"],
        "pages": context["pages"],
        "page_numbers": page_numbers,
        "next": context["next"],
        "previous": context["previous"],
        "has_next": context["has_next"],
        "has_previous": context["has_previous"],
        "show_first": 1 not in page_numbers,
        "show_last": context["pages"] not in page_numbers,
    }
        
register.inclusion_tag("paginator.html", takes_context=True)(paginator)

register.filter('nthitem', nthitem)
register.filter('lessthan', lessthan)
register.filter('replacePostImagesArticle', replacePostImagesArticle)
register.filter('replacePostImagesGallery', replacePostImagesGallery)
register.filter('replaceMediaUrl', replaceMediaUrl)
