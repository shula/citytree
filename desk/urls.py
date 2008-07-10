from django.conf.urls.defaults import *


members_csv_url = 'members/csv/'
# XXX: desk shouldn't be in that, it's determined elsewhere
members_csv_absolute_url = '/desk/%s' % members_csv_url

urlpatterns = patterns('',
    (r'^$', 'desk.views.tree_trunk'),
    (r'^login/$', 'django.contrib.auth.views.login', {'template_name': 'desk/login.html'}),
    (r'^logout/$', 'django.contrib.auth.views.logout', {'next_page': '/desk/'}),
    (r'^help/$', 'desk.views.help_view'),
    (r'^mybranches/(?P<blog_slug>\w+)/$', 'desk.views.blogdetail'),
    # NOTE: posts are changed through the same urls, wether they are a workshop or regular.
    (r'^branches/(?P<blog_slug>\w+)/createPost/$', 'desk.views.create_edit_blog_post'),
    (r'^editPost/(?P<post_id>\d+)/$', 'desk.views.create_edit_blog_post'),
    (r'^deletePost/(?P<post_id>\d+)/$', 'desk.views.delete_blog_post'),
    # members
    ('^^%s$' % members_csv_url, 'desk.views.members_csv'),
    # workshop
    (r'^workshop/(?P<workshop_slug>\w+)/addEvent/$', 'desk.views.create_edit_workshop_event'),
    (r'^workshop/(?P<workshop_slug>\w+)/editEvent/(?P<we_id>\d+)/$', 'desk.views.create_edit_workshop_event'),
    (r'^workshop/deleteEvent/(?P<we_id>\d+)/$', 'desk.views.delete_workshop_event'),
    (r'^workshop/(?P<workshop_slug>\w+)/(?P<we_id>\d+)/csv/$', 'desk.views.get_workshop_event_registered_csv'),
)
