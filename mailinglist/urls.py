
from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^join/$', 'mailinglist.views.join'),
    (r'^confirm/(?P<confirm_code>.*)$','citytree.mailinglist.views.confirm'),
)

