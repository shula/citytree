from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^register/$', 'workshop.views.register'),
    (r'^register/(?P<workshop_slug>.+)/$', 'workshop.views.register'),
)

