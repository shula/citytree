from django.conf.urls.defaults import *
from cityblog.models import blog
from django.contrib.comments.models import FreeComment
from django.views.generic import list_detail
from django.views.generic.simple import redirect_to


blog_dict = {
    'queryset': blog.objects.all(),
    'template_name': 'cityblog/blogs_main_page.html'
}

urlpatterns = patterns('',
    #(r'^$', list_detail.object_list, blog_dict ),
    (r'^$', redirect_to, {'url':'/'}),
    (r'^(?P<blog_slug>\w+)/?$', 'cityblog.views.show_blog'),
    (r'^comments/', include('django.contrib.comments.urls.comments')),
    (r'^posts/(?P<post_id>.*)/$', 'cityblog.views.display_post'),
    (r'^preview_post/(?P<post_id>.*)/$', 'cityblog.views.display_post', {'preview' : True})
)
