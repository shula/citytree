from django.conf.urls.defaults import *
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to

from cityblog.models import Blog

blog_dict = {
    'queryset': Blog.objects.all(),
    'template_name': 'cityblog/blogs_main_page.html'
}

urlpatterns = patterns('',
    #(r'^$', list_detail.object_list, blog_dict ),
    (r'^$', redirect_to, {'url':'/'}),
    (r'^search$', 'cityblog.views.search'),
    (r'^(?P<blog_slug>\w+)/?$', 'cityblog.views.show_blog_or_workshop'),
#    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^posts/(?P<post_id>.*)/$', 'cityblog.views.display_post'),
    (r'^preview_post/(?P<post_id>.*)/$', 'cityblog.views.display_post', {'preview' : True}),
)
