from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^ban_request/(?P<hash>.*)/$', 'spamdetector.views.ban_request'),
    (r'^hide_comment/(?P<hash>.*)/$', 'spamdetector.views.hide_comment'),
)
