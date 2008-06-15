from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^register/$', 'workshop.views.register'),
    (r'^register/(?P<workshop_slug>.+)/(?P<workshop_event_id>\d+)/$', 'workshop.views.register'),
    (r'^register/(?P<workshop_slug>.+)/$', 'workshop.views.register'),
    (r'^(?P<workshop_slug>.+)/$', 'workshop.views.display_workshop'),
)

