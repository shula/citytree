from django.contrib.sites.models import Site
from cityblog.models import Blog, Post, Flag, Subject

def add_render_variables(d, obj=None):
    """ this function is used to add variables to several views request context's,
    right now just for like / addtoany function.
    """
    # TODO: put some stuff (like_href) into context variables
    # the menu's blogs are based on the db blogs, taken from displayed_blogs.
    d['displayed_blogs'] = Blog.objects.filter(display_in_menu=True)
    rest = '/'
    if obj:
        rest = obj.get_absolute_url()
    d['like_href'] = 'http://%s%s' % (Site.objects.get_current().domain, rest)
    return d

