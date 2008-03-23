from django.conf.urls.defaults import *
from cityblog.models import blog
from django.contrib.comments.models import FreeComment


blog_dict = {
    'queryset': blog.objects.all(),
}

urlpatterns = patterns('',
    (r'^$', 'cityblog.views.main_page' ),
    (r'^(?P<blog_slug>\w+)/$', 'cityblog.views.show_blog'),
    (r'^comments/', include('django.contrib.comments.urls.comments')),
    (r'^posts/(?P<post_id>.*)/$', 'cityblog.views.display_post'),
    (r'^preview_post/(?P<post_id>.*)/$', 'cityblog.views.display_post', {'preview' : True})
)
