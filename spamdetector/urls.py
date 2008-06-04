from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^ban_request/(?P<hash>.*)/$', 'spamdetector.views.ban_request'),
)
