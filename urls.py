from django.conf.urls.defaults import *
from django.contrib import admin
from citytree.cityblog.feeds import LatestPosts
import settings

#admin.autodiscover() # import all app.admin modules
import accounts.admin
import cityblog.admin
import workshop.admin
import citymail.admin
#import django.contrib.comments.admin # I have my own ModelAdmin
import django.contrib.flatpages.admin
import django.contrib.auth.admin
import django.contrib.redirects.admin
import frontpage.admin
import citycomments.admin
import spamdetector.admin

handler500 = 'citytree.views.handler500'

feeds = {
    'posts' : LatestPosts # the actual url may be posts/tami and that filters by slug.
}

urlpatterns = patterns('',
    # Example:
    # (r'^citytreesite/', include('citytreesite.apps.foo.urls.foo')),

    (r'^admin/(.*)',  admin.site.root),
    (r'^feeds/(?P<url>.*)/$', 'django.contrib.syndication.views.feed', {'feed_dict': feeds}),
    (r'^feeds$',      'citytree.cityblog.feeds.main_page'),
    (r'^forum/',      include('forum.urls')),
    (r'^uptime_openacs/$', 'citytree.views.uptime_openacs'),
    (r'^desk/',       include('citytree.desk.urls')),
    (r'^blogs/',      'citytree.cityblog.views.redirect_to_branches'),
    (r'^branches/',      include('citytree.cityblog.urls')),
    (r'^spamdetector/',include('citytree.spamdetector.urls')),
    (r'^accounts/',   include('citytree.accounts.urls')),
    (r'^workshop/',   include('citytree.workshop.urls')),
    (r'^mailinglist/',   include('citytree.mailinglist.urls')),
    (r'^subjects/(?P<subject_slug>.*)/$','citytree.cityblog.views.subject_view'),
    (r'^ajax/',       include('citytree.ajax.urls')),
#     (r'^comments/postfree/$','citytree.cityblog.views.postfree'), # this is the wrong one (move to correct namespace. do not use comments module - already exists in django and django doesn't like two modules with the same name, even if the full name is different)
    (r'^comments/', include('django.contrib.comments.urls')),
    (r'^citycomments/', include('citytree.citycomments.urls')), # post is here
    (r'^send_feedback/$', 'cityblog.views.send_feedback'),
    (r'^', include('citytree.frontpage.urls')),
)

for y in [x for x in [x.urlconf_name for x in urlpatterns if hasattr(x, 'urlconf_name')] if x == 'django.contrib.comments.urls.comments']:
    import pdb; pdb.set_trace()

if settings.SERVE_SITEMEDIA_FROM_DJANGO:
    urlpatterns += patterns('',(r'^siteMedia/(?P<path>.*)$', 'django.views.static.serve', {'document_root': '/home/citytree/siteMedia'}))

