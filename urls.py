from django.conf.urls.defaults import *
from django.contrib.comments.models import FreeComment
from citytree.cityblog.feeds import LatestPosts

feeds = {
    'posts' : LatestPosts # the actual url may be posts/tami and that filters by slug.
}

urlpatterns = patterns('',
    # Example:
    # (r'^citytreesite/', include('citytreesite.apps.foo.urls.foo')),

    # Uncomment this for admin:
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^feeds$', 'citytree.cityblog.feeds.main_page'),
    (r'^forum/', include('forum.urls')),
    (r'^uptime_openacs/$', 'citytree.views.uptime_openacs'),
    (r'^admin/', include('django.contrib.admin.urls')),
    (r'^desk/', include('citytree.desk.urls')),
    (r'^blogs/', include('citytree.cityblog.urls')),
    (r'^spamdetector/', include('citytree.spamdetector.urls')),
    (r'^subjects/(?P<subject_slug>.*)/$', 'citytree.cityblog.views.subject_view'),
    (r'^ajax/', include('citytree.ajax.urls')),
#     (r'^comments/postfree/$', 'citytree.cityblog.views.postfree'), # this is the wrong one (move to correct namespace. do not use comments module - already exists in django and django doesn't like two modules with the same name, even if the full name is different)
    (r'^comments/', include('django.contrib.comments.urls.comments')),
    (r'^send_feedback/$', 'cityblog.views.send_feedback'),
    (r'^', include('citytree.frontpage.urls')),
)

