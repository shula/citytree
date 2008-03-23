from django.conf.urls.defaults import *
from django.contrib.comments.models import FreeComment

urlpatterns = patterns('',
    # Example:
    # (r'^citytreesite/', include('citytreesite.apps.foo.urls.foo')),

    # Uncomment this for admin:
     (r'^admin/', include('django.contrib.admin.urls')),
     (r'^desk/', include('citytree.desk.urls')),
     (r'^blogs/', include('citytree.cityblog.urls')),
     (r'^subjects/(?P<subject_slug>.*)/$', 'citytree.cityblog.views.subject_view'),
     (r'^ajax/', include('citytree.ajax.urls')),
     (r'^comments/', include('django.contrib.comments.urls.comments')),
     (r'^send_feedback/$', 'cityblog.views.send_feedback'),
     (r'^', include('citytree.frontpage.urls')),
)
