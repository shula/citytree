from django.conf.urls.defaults import *

urlpatterns = patterns('',
    # Example:
    # (r'^citytreesite/', include('citytreesite.apps.foo.urls.foo')),

    # Uncomment this for admin:
     (r'^calendar/$', 'ajax.views.calendar' ),
)
