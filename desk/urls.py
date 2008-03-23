from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^$', 'desk.views.tree_trunk'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'desk/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/desk/'}),
    (r'^help/$', 'desk.views.help_view'),
    (r'^mybranches/(?P<blog_slug>\w+)/$', 'desk.views.blogdetail'),
    (r'^blogs/(?P<blog_slug>\w+)/createPost/$', 'desk.views.create_edit_blog_post'),
    (r'^editPost/(?P<post_id>\d+)/$', 'desk.views.create_edit_blog_post'),
    (r'^deletePost/(?P<post_id>\d+)/$', 'desk.views.delete_blog_post'),
)
